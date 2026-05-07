import pygame
import sys
import numpy as np
import time
from loader import load_assembly, get_bounding_box
from engine_3d import Engine3D, apply_part_kinematics
from ui_components import Slider, TelemetryPanel, RealTimeGraph, COLOR_BG, COLOR_ACCENT

# Configuration
FPS = 60
MODELS_DIR = "models"

def main():
    pygame.init()
    
    # Enable Fullscreen and get native resolution
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("EXO-PIERNA EXHIBITION MODE v6.0")
    clock = pygame.time.Clock()
    
    # 1. Load Assembly
    parts_data = load_assembly(MODELS_DIR)
    if not parts_data:
        print("Error: No STL files found.")
        sys.exit(1)
    
    # 2. Categorization by Side and Role
    legs = {'Left': [], 'Right': []}
    
    for name, verts in parts_data.items():
        if "easy print" in name.lower():
            base_name = name.lower().replace(" (easy print version)", "")
            if any(base_name in k.lower() for k in parts_data.keys() if k != name):
                continue
        
        v = verts.copy()
        # Vertical Correction (Z-up to Y-up)
        old_y = v[:, 1].copy()
        old_z = v[:, 2].copy()
        v[:, 1] = old_z
        v[:, 2] = -old_y
        
        is_left = "left" in name.lower() or "(l)" in name.lower()
        side = 'Left' if is_left else 'Right'
        
        role = "MID"
        if "lower" in name.lower() or "foot" in name.lower():
            role = "BOT"
        elif "upper" in name.lower() or "mount" in name.lower() or "sleeve" in name.lower():
            role = "TOP"
        elif "mid" in name.lower() or "thigh" in name.lower():
            role = "MID"
            
        legs[side].append({
            "name": name,
            "verts": v,
            "role": role,
            "side": side
        })

    # 3. VERTICAL STACKING / SEGMENTATION
    temp_processed = []
    all_parts_count = sum(len(parts) for parts in legs.values())
    
    for side in ['Left', 'Right']:
        side_parts = legs[side]
        if not side_parts: continue
        
        if all_parts_count == 1:
            p = side_parts[0]
            v = p["verts"]
            y_min, y_max = v[:, 1].min(), v[:, 1].max()
            h = y_max - y_min
            v_top = v[v[:, 1] > y_min + 0.7 * h].copy()
            v_mid = v[(v[:, 1] <= y_min + 0.7 * h) & (v[:, 1] > y_min + 0.3 * h)].copy()
            v_bot = v[v[:, 1] <= y_min + 0.3 * h].copy()
            side_parts = [
                {"name": p["name"]+"_TOP", "verts": v_top, "role": "TOP", "side": side},
                {"name": p["name"]+"_MID", "verts": v_mid, "role": "MID", "side": side},
                {"name": p["name"]+"_BOT", "verts": v_bot, "role": "BOT", "side": side}
            ]
        
        h_offset = -100 if side == 'Left' else 100
        for p in side_parts:
            p["verts"][:, 0] += h_offset
            temp_processed.append(p)

    # 4. GLOBAL CENTERING & SCALING
    all_stacked_verts = np.concatenate([p["verts"] for p in temp_processed])
    min_c, max_c = get_bounding_box(all_stacked_verts)
    global_center = (min_c + max_c) / 2
    total_height = max_c[1] - min_c[1]
    total_width = max_c[0] - min_c[0]
    fit_scale = 3.5 / max(total_height, total_width)

    processed_parts = []
    for p in temp_processed:
        p["verts"] = (p["verts"] - global_center) * fit_scale
        n_tris = len(p["verts"]) // 3
        dec = max(1, n_tris // 1500) 
        tri_indices = np.arange(0, n_tris, dec)
        v_indices = np.empty(len(tri_indices) * 3, dtype=np.int32)
        for i, idx in enumerate(tri_indices):
            v_indices[i*3] = idx * 3
            v_indices[i*3+1] = idx * 3 + 1
            v_indices[i*3+2] = idx * 3 + 2
        p["verts"] = p["verts"][v_indices].copy()
        p["group"] = 2 if p["role"] == "BOT" else (1 if p["role"] == "MID" else 0)
        processed_parts.append(p)

    # Pivots
    all_final = np.concatenate([p["verts"] for p in processed_parts])
    y_min, y_max = all_final[:, 1].min(), all_final[:, 1].max()
    mids = [p for p in processed_parts if p["role"] == "MID"]
    y_pivot_knee = np.concatenate([p["verts"] for p in mids])[:, 1].min() if mids else y_min + (y_max-y_min)*0.4
    y_pivot_hip = y_max - 0.2

    engine = Engine3D(WIDTH, HEIGHT)
    engine.viewer_distance = 6.0
    
    sliders = [
        Slider(50, HEIGHT//2 - 150, 250, 10, 0, 90, "Flexión Rodilla", 0),
        Slider(50, HEIGHT//2 - 70, 250, 10, -0.2, 0.2, "Ajuste Altura", 0),
        Slider(50, HEIGHT//2 + 10, 250, 10, -10, 20, "Abducción Cadera", 0)
    ]
    
    telemetry = TelemetryPanel(WIDTH - 350, 50, 300, 300)
    graphs = [
        RealTimeGraph(50, HEIGHT - 250, 250, 60, (0, 255, 200), "Dinámica Rodilla"),
        RealTimeGraph(50, HEIGHT - 120, 250, 60, (255, 0, 255), "Dinámica Abducción")
    ]
    battery = 100.0
    demo_mode = False
    orbit_x = 0
    orbit_y = 45
    mouse_dragging = False
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == pygame.K_d: demo_mode = not demo_mode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not any(s.rect.collidepoint(event.pos) for s in sliders):
                        mouse_dragging = True
                if event.button == 4: engine.viewer_distance = max(2.0, engine.viewer_distance - 0.5)
                if event.button == 5: engine.viewer_distance = min(15.0, engine.viewer_distance + 0.5)
            if event.type == pygame.MOUSEBUTTONUP: mouse_dragging = False
            if event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    orbit_y += event.rel[0] * 0.5
                    orbit_x -= event.rel[1] * 0.5
            for s in sliders: s.handle_event(event)
        
        if demo_mode:
            t = pygame.time.get_ticks() / 1000.0
            sliders[0].val = 45 + 40 * np.sin(t * 1.5)
            sliders[1].val = 0.1 * np.sin(t * 1.2)
            sliders[2].val = 5 * np.sin(t * 0.8)
            orbit_y += 0.3
            
        knee_a = sliders[0].val
        ext = sliders[1].val
        abd_val = sliders[2].val
        graphs[0].update(knee_a)
        graphs[1].update(abd_val)
        
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, (50, 50, 70), (0, 0, 350, HEIGHT))
        
        for p in processed_parts:
            abd = -abd_val if p["side"] == 'Left' else abd_val
            kin_verts = apply_part_kinematics(
                p["verts"], 
                knee_a if p["group"] == 2 else 0,
                ext if p["group"] == 2 else 0,
                abd,
                1 if p["group"] >= 1 else 0,
                y_pivot_knee, y_pivot_hip
            )
            
            triangles = engine.render(kin_verts, orbit_x, orbit_y, 0, 0.6, 0, 0, return_triangles=True)
            color = (0, 255, 255) if p["side"] == 'Left' else (255, 100, 255)
            line_color = (int(color[0]*0.9), int(color[1]*0.9), int(color[2]*0.9))
            
            for tri in triangles:
                if np.all(np.isfinite(tri)):
                    if all(350 <= pt[0] < WIDTH and 0 <= pt[1] < HEIGHT for pt in tri):
                        points = [(int(pt[0]), int(pt[1])) for pt in tri]
                        pygame.draw.lines(screen, line_color, True, points, 2)

        if any(s.grabbed for s in sliders) or demo_mode: battery -= 0.005
        tele_data = {
            "MODO": "EXHIBICIÓN" if demo_mode else "CONTROL",
            "Batería": f"{max(0, battery):.1f} %",
            "Flexión": f"{knee_a:.1f}°",
            "Extensión": f"{ext*100:+.1f} cm",
            "Abducción": f"{abd_val:.1f}°",
            "Cámara": f"D:{engine.viewer_distance:.1f} R:{orbit_y%360:.0f}°"
        }
        for s in sliders: s.draw(screen)
        for g in graphs: g.draw(screen)
        telemetry.draw(screen, tele_data)
        info = pygame.font.SysFont('Consolas', 14).render(f"FPS: {clock.get_fps():.1f} | 'D' Demo | Mouse: Orbit/Zoom | ESC salir", True, (150, 150, 150))
        screen.blit(info, (WIDTH - 450, HEIGHT - 30))
        pygame.display.flip()

if __name__ == "__main__":
    main()
