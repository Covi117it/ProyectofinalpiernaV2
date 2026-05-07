import pygame

# Colors (High-Contrast Exhibition Theme)
COLOR_BG = (30, 30, 40)        # Lighter background
COLOR_PANEL = (45, 45, 60)     # More distinct panel
COLOR_ACCENT = (0, 255, 220)   # Brighter Cyan
COLOR_TEXT = (255, 255, 255)   # Pure White text
COLOR_SLIDER_BG = (70, 70, 90) # Visible slider tracks
COLOR_SLIDER_KNOB = (255, 255, 255) # White knobs for maximum visibility
COLOR_DANGER = (255, 100, 100)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, label, initial_val=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val if initial_val is not None else min_val
        self.label = label
        self.grabbed = False
        self.font = pygame.font.SysFont('Consolas', 16)
        
    def draw(self, screen):
        # Draw Label
        txt = self.font.render(f"{self.label}: {self.val:.1f}", True, COLOR_TEXT)
        screen.blit(txt, (self.rect.x, self.rect.y - 25))
        
        # Draw Track
        pygame.draw.rect(screen, COLOR_SLIDER_BG, self.rect, border_radius=5)
        
        # Draw Progress
        fill_w = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
        pygame.draw.rect(screen, COLOR_ACCENT, fill_rect, border_radius=5)
        
        # Draw Knob
        knob_x = self.rect.x + fill_w
        pygame.draw.circle(screen, COLOR_SLIDER_KNOB, (knob_x, self.rect.centery), 10)
        
    @property
    def rect_with_margin(self):
        # Helper for mouse interaction
        return self.rect.inflate(0, 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION:
            if self.grabbed:
                pos_x = max(self.rect.x, min(event.pos[0], self.rect.right))
                self.val = self.min_val + (pos_x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)

class RealTimeGraph:
    def __init__(self, x, y, w, h, color, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.label = label
        self.data = [0] * 50
        self.font = pygame.font.SysFont('Consolas', 14)

    def update(self, val):
        self.data.pop(0)
        self.data.append(val)

    def draw(self, screen):
        pygame.draw.rect(screen, (30, 30, 45), self.rect, border_radius=5)
        pygame.draw.rect(screen, (50, 50, 70), self.rect, width=1, border_radius=5)
        
        txt = self.font.render(self.label, True, COLOR_TEXT)
        screen.blit(txt, (self.rect.x, self.rect.y - 20))

        if len(self.data) > 1:
            points = []
            max_v = max(self.data) if max(self.data) != min(self.data) else 1
            min_v = min(self.data)
            range_v = max_v - min_v if max_v != min_v else 1
            
            for i, v in enumerate(self.data):
                px = self.rect.x + (i / (len(self.data)-1)) * self.rect.width
                # Normalize v to 0-1
                norm_v = (v - min_v) / range_v
                py = self.rect.bottom - norm_v * self.rect.height
                points.append((px, py))
            
            if len(points) >= 2:
                pygame.draw.lines(screen, self.color, False, points, 2)

class TelemetryPanel:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.font_title = pygame.font.SysFont('Consolas', 22, bold=True)
        self.font_data = pygame.font.SysFont('Consolas', 18)
        
    def draw(self, screen, data):
        # Background
        pygame.draw.rect(screen, COLOR_PANEL, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_ACCENT, self.rect, width=2, border_radius=10)
        
        # Title
        title = self.font_title.render("SISTEMA TELEMETRÍA", True, COLOR_ACCENT)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))
        
        y_offset = 70
        for key, value in data.items():
            # Label
            label_surf = self.font_data.render(f"{key}:", True, COLOR_TEXT)
            screen.blit(label_surf, (self.rect.x + 20, self.rect.y + y_offset))
            
            # Value (formatted)
            val_str = str(value)
            val_surf = self.font_data.render(val_str, True, COLOR_ACCENT)
            screen.blit(val_surf, (self.rect.x + 200, self.rect.y + y_offset))
            
            y_offset += 40
            
        # Connectivity status (Simulated Pulse)
        status_color = COLOR_ACCENT if pygame.time.get_ticks() % 1000 < 800 else COLOR_BG
        pygame.draw.circle(screen, status_color, (self.rect.right - 30, self.rect.y + 35), 8)
        conn_txt = self.font_data.render("BT-LINK", True, COLOR_TEXT)
        screen.blit(conn_txt, (self.rect.right - 110, self.rect.y + 25))
