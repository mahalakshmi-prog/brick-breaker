import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)
BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle = Paddle(width // 2 - 50, height - 30, 100, 14)

        self.ball = Ball(width // 2, height - 50, radius=8)
        self.ball.vx, self.ball.vy = 4, -4

        self.rows, self.cols = 5, 8
        self.bricks = self._build_bricks(self.rows, self.cols)

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False
        self.result = None  # "win" or "lose"
        # Current difficulty (default = Medium)
        self.difficulty = "medium"

        # Ball speed for the selected difficulty
        self.ball_speed = 4

        # Flag used by main.py
        self.exit_game = False
        # -------------------------------
        # Load sound effects
        # -------------------------------
        self.paddle_sound = pygame.mixer.Sound("assets/paddle.wav")
        self.brick_sound = pygame.mixer.Sound("assets/brick.wav")
        self.end_sound = pygame.mixer.Sound("assets/gameover.wav")
        

    def _build_bricks(self, rows, cols):
        bricks = []
        margin, gap, top = 30, 6, 60
        brick_w = (self.width - margin * 2 - gap * (cols - 1)) // cols
        brick_h = 22

        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)
                bricks.append(Brick(x, y, brick_w, brick_h))

        return bricks

    def handle_event(self, event):
        # This game only needs continuously-held-key input for the
        # paddle, handled in handle_input each frame.
        pass

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(-self.paddle.speed, self.width)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(self.paddle.speed, self.width)

    # ------------------------------------------------------------------
    # NEW HELPER FUNCTION
    # ------------------------------------------------------------------
    # Determines whether the ball hit the rectangle from the side
    # or from the top/bottom.
    #
    # If overlap is smaller in X direction -> horizontal collision
    # -> reverse vx.
    #
    # Otherwise -> vertical collision -> reverse vy.
    # ------------------------------------------------------------------
    def _resolve_collision(self, rect):
        ball_rect = self.ball.rect()

        overlap_left = ball_rect.right - rect.left
        overlap_right = rect.right - ball_rect.left
        overlap_top = ball_rect.bottom - rect.top
        overlap_bottom = rect.bottom - ball_rect.top

        overlap_x = min(overlap_left, overlap_right)
        overlap_y = min(overlap_top, overlap_bottom)

        if overlap_x < overlap_y:
            # Hit left/right side
            self.ball.vx *= -1
        else:
            # Hit top/bottom
            self.ball.vy *= -1

    def update(self):
        if self.game_over:
            return

        self.ball.move()

        # Wall collisions
        if (
            self.ball.x - self.ball.radius <= 0
            or self.ball.x + self.ball.radius >= self.width
        ):
            self.ball.vx *= -1

        if self.ball.y - self.ball.radius <= 0:
            self.ball.vy *= -1

        # --------------------------------------------------------------
        # UPDATED PADDLE COLLISION
        # Uses side-aware collision detection instead of always
        # reversing vy.
        # --------------------------------------------------------------
        if self.ball.rect().colliderect(self.paddle.rect()):
            self._resolve_collision(self.paddle.rect())
            self.paddle_sound.play()

        # --------------------------------------------------------------
        # UPDATED BRICK COLLISION
        # Uses side-aware collision detection instead of always
        # reversing vy.
        # --------------------------------------------------------------
        for brick in self.bricks:
            if brick.alive and self.ball.rect().colliderect(brick.rect()):
                brick.alive = False
                self.score += 1

                self.brick_sound.play()
                self._resolve_collision(brick.rect())
                break

        # Ball fell below screen
        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
            else:
                self._reset_ball()

        # Win condition
        if all(not b.alive for b in self.bricks):
            self.game_over = True
            self.result = "win"

    def _reset_ball(self):
        self.ball.x = self.width // 2
        self.ball.y = self.height - 50
        self.ball.vx = 4
        self.ball.vy = -4
        # ------------------------------------------------------------------
    # NEW METHOD
    # Displays an end screen when the player wins or loses.
    # Shows:
    #   - YOU WIN! / GAME OVER
    #   - Final Score
    #   - Press ENTER to continue
    #
    # Waits until ENTER is pressed or the window is closed.
    # ------------------------------------------------------------------
    def _restart_game(self):

    # Paddle size based on difficulty
     if self.difficulty == "easy":
        paddle_width = 140
     elif self.difficulty == "hard":
        paddle_width = 70
     else:
        paddle_width = 100

     self.paddle = Paddle(
        self.width // 2 - paddle_width // 2,
        self.height - 30,
        paddle_width,
        14,
    )

     self.ball = Ball(
        self.width // 2,
        self.height - 50,
        radius=8,
    )

     self.ball.vx = self.ball_speed
     self.ball.vy = -self.ball_speed

     self.bricks = self._build_bricks(self.rows, self.cols)

     self.score = 0
     self.lives = 3

     self.game_over = False
     self.result = None
     self._game_over_logged = False
    
    def _show_end_screen(self, screen):

        title_font = pygame.font.SysFont("Arial", 56, bold=True)
        score_font = pygame.font.SysFont("Arial", 34)
        info_font = pygame.font.SysFont("Arial", 26)

        if self.result == "win":
            title = "YOU WIN!"
            color = (80, 220, 120)
        else:
            title = "GAME OVER"
            color = (220, 80, 80)

        waiting = True
        clock = pygame.time.Clock()

        while waiting:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.exit_game = True
                    waiting = False

                elif event.type == pygame.KEYDOWN:

            # Easy
                    if event.key == pygame.K_1:
                        self.difficulty = "easy"
                        self.ball_speed = 2
                        self._restart_game()
                        waiting = False

            # Medium
                    elif event.key == pygame.K_2:
                        self.difficulty = "medium"
                        self.ball_speed = 4
                        self._restart_game()
                        waiting = False

            # Hard
                    elif event.key == pygame.K_3:
                        self.difficulty = "hard"
                        self.ball_speed = 6
                        self._restart_game()
                        waiting = False

            # Exit
                    elif event.key == pygame.K_ESCAPE:
                        self.exit_game = True
                        waiting = False

            screen.fill(BG)

            title_text = title_font.render(title, True, color)
            score_text = score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE,
            )
            info_text = info_font.render(
                "1-Easy   2-Medium   3-Hard   ESC-Exit",
                True,
                WHITE,
            )

            screen.blit(
                title_text,
                (
                    (self.width - title_text.get_width()) // 2,
                    self.height // 2 - 80,
                ),
            )

            screen.blit(
                score_text,
                (
                    (self.width - score_text.get_width()) // 2,
                    self.height // 2,
                ),
            )

            screen.blit(
                info_text,
                (
                    (self.width - info_text.get_width()) // 2,
                    self.height // 2 + 60,
                ),
            )

            pygame.display.flip()
            clock.tick(60)

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(screen, WHITE, self.paddle.rect())
        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.ball.x), int(self.ball.y)),
            self.ball.radius,
        )

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                pygame.draw.rect(screen, color, brick.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

                # --------------------------------------------------------------
        # UPDATED GAME OVER HANDLING
        #
        # Instead of printing the result to the terminal,
        # display a proper Pygame end screen.
        # The screen waits until the player presses ENTER
        # or closes the window.
        # --------------------------------------------------------------
        if self.game_over and not getattr(self, "_game_over_logged", False):
            self.end_sound.play()
            pygame.display.flip()
            self._show_end_screen(screen)
            self._game_over_logged = True