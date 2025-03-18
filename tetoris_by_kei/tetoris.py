import pygame
import random
import sys


def main():
    # Pygame 초기화
    pygame.init()
    pygame.mixer.init()
    
    # 배경음악 추가
    pygame.mixer.music.load("tetoriss.mp3")  #""안에 재생할 음악의 위치적기
    pygame.mixer.music.set_volume(0.1)  # 음량을 50%로 설정
    pygame.mixer.music.play(-1)

    # 게임 루프 시작
    game_loop()

# 블록 크기 및 그리드 크기
# 메인 그리드 크기
GRID_WIDTH = 10   # 가로 블록 수
GRID_HEIGHT = 20  # 세로 블록 수
BLOCK_SIZE = 30
grid_x_offset = 6  # 그리드 시작 오프셋(왼쪽에서 6블록 오른쪽)


# 화면 설정
SCREEN_WIDTH = (GRID_WIDTH + 12) * BLOCK_SIZE  # 추가 여유 공간 포함
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)

# 테트리스 블록 모양 정의
SHAPES = [
    [[1, 1, 1, 1]],           # I 모양
    [[1, 1],
     [1, 1]],                # O 모양
    [[0, 1, 0],
     [1, 1, 1]],             # T 모양
    [[1, 0, 0],
     [1, 1, 1]],             # L 모양
    [[0, 0, 1],
     [1, 1, 1]],             # J 모양
    [[1, 1, 0],
     [0, 1, 1]],             # S 모양
    [[0, 1, 1],
     [1, 1, 0]],             # Z 모양
]

# 테트리스 블록 모양에 따른 지정 색상
SHAPES_COLORS = [
    (173, 216, 230),  # I: 민트 (LightBlue 색상)
    (255, 255, 0),    # O: 노랑
    (147, 112, 219),  # T: 연보라 (MediumPurple 색상)
    (255, 165, 0),    # L: 주황
    (135, 206, 250),  # J: 하늘 (SkyBlue 색상)
    (144, 238, 144),  # S: 연두 (LightGreen 색상)
    (220, 20, 60),    # Z: 다홍색 (Crimson 색상)
]



# 게임 상태: 그리드(고정된 블록)와 점수
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
score = 0

# 홀드 상태 변수
held_block = None       # 현재 홀드된 블록
can_hold = True         # 한 턴에 한 번만 홀드 가능

# 블록 클래스
class Block:
    def __init__(self, shape_index, extra_argument = None):
        self.shape = SHAPES[shape_index]
        self.color = SHAPES_COLORS[shape_index]
        self.extra_argument = extra_argument
        # 초기 위치: 중앙에서 시작
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def get_coords(self):
        coords = []
        for row_index, row in enumerate(self.shape):
            for col_index, value in enumerate(row):
                if value:
                    coords.append((self.x + col_index, self.y + row_index))
        return coords

# 게임 오버 확인 함수
def check_game_over():
    for x in range(GRID_WIDTH):
        if grid[0][x] != 0:
            return True
    return False

# 충돌 체크
def check_collision(block):
    for x, y in block.get_coords():
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and grid[y][x]):
            return True
    return False

# 현재 블록을 그리드에 고정
def freeze_block(block):
    for x, y in block.get_coords():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = block.color

# 가득 찬 줄 삭제 및 점수 증가
def clear_lines():
    global grid, score
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    grid = [[0] * GRID_WIDTH for _ in range(lines_cleared)] + new_grid

    if lines_cleared == 1:
        score += 100
    elif lines_cleared == 2:
        score += 300
    elif lines_cleared == 3:
        score += 500
    elif lines_cleared == 4:
        score += 800

# 점수 표시
def draw_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

# 게임 초기화 (재시작 등)
def reset_game():
    global grid, score, held_block, can_hold
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    score = 0
    held_block = None
    can_hold = True

def game_over_screen():
    font = pygame.font.SysFont(None, 48)
    text = font.render("Game Over", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 50))  # "Game Over" 중앙 배치

    # 점수 표시
    score_font = pygame.font.SysFont(None, 36)
    score_text = score_font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 10))  # 점수는 아래쪽에 표시

    # 재시작 및 종료 안내
    restart_font = pygame.font.SysFont(None, 24)
    restart_text = restart_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + 50))  # 안내 메시지 표시

    pygame.mixer.music.stop()  # 음악 중지
    pygame.display.flip()

# 다음 블록 표시 (미리보기)
def draw_next_block(block):
    next_block_x = GRID_WIDTH + 7  # 그리드 오른쪽에 위치
    next_block_y = 3
    for row_index, row in enumerate(block.shape):
        for col_index, value in enumerate(row):
            if value:
                rect = pygame.Rect(
                    (next_block_x + col_index) * BLOCK_SIZE,
                    (next_block_y + row_index) * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(screen, block.color, rect)
                pygame.draw.rect(screen, WHITE, rect, 1)

def draw_background_grid():
    # 전체 화면의 크기 계산 (그리드 크기를 넘어 화면 전체로 확장)
    grid_width_px = GRID_WIDTH * BLOCK_SIZE
    grid_height_px = GRID_HEIGHT * BLOCK_SIZE
    
    # 투명도 지원 Surface 생성 (pygame.SRCALPHA 사용)
    grid_surface = pygame.Surface((grid_width_px, grid_height_px), pygame.SRCALPHA)
    grid_surface.set_alpha(35)  # 투명도 설정 (0=완전투명, 255=불투명)

    # 메인 그리드만 그리기
    for row in range(0, GRID_HEIGHT * BLOCK_SIZE, BLOCK_SIZE):
        for col in range(0, GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE):
            rect = pygame.Rect(col, row, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(grid_surface, WHITE, rect, 1)  # 테두리만 그림

    # 메인 그리드 위치에 배치
    grid_x_offset = 6 * BLOCK_SIZE  # 예: x 축 오프셋 조정
    screen.blit(grid_surface, (grid_x_offset, 0))

# 고정된 블록 및 현재 블록, 배경 그리드까지 모두 그리기  
def draw_grid_with_blocks(current_block):
    # 1. 배경 그리드 (투명 테두리 적용)
    draw_background_grid()

    # 메인 그리드의 가로 시작 위치 (오프셋)
    grid_x_offset = 6  # 블록 5칸만큼 오른쪽으로 이동
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid[row][col]:
                rect = pygame.Rect((grid_x_offset + col) * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, grid[row][col], rect)
                pygame.draw.rect(screen, WHITE, rect, 1)

    # 3. 현재 블록 렌더링
    for x, y in current_block.get_coords():
        rect = pygame.Rect((grid_x_offset + x) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, current_block.color, rect)
        pygame.draw.rect(screen, WHITE, rect, 1)


def draw_held_block(block):
    if block is not None:
        # 홀드 블록 공간의 위치 설정 (그리드 왼쪽)
        held_block_x = 1  # 그리드 왼쪽 가장자리
        held_block_y = 3
        for row_index, row in enumerate(block.shape):
            for col_index, value in enumerate(row):
                if value:
                    rect = pygame.Rect((held_block_x + col_index) * BLOCK_SIZE,
                                       (held_block_y + row_index) * BLOCK_SIZE,
                                       BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, block.color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)
        
        # "HOLD" 텍스트 추가
        font = pygame.font.SysFont(None, 24)
        text = font.render("HOLD", True, WHITE)
        screen.blit(text, (held_block_x * BLOCK_SIZE, (held_block_y - 1) * BLOCK_SIZE))

                    
# --- 게임 상태 변수 ---
is_paused = False  # 처음에는 일시 정지 상태가 아님

# --- "PAUSED" 메시지를 화면에 표시 ---
def draw_pause_message():
    font = pygame.font.SysFont(None, 48)
    pause_text = font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                             SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))

def calculate_ghost_block(block):
    ghost_block = Block(0)
    ghost_block.shape = block.shape
    ghost_block.color = (200, 200, 200)  # 고스트 블록 색상
    ghost_block.x = block.x
    ghost_block.y = block.y

    # 충돌하지 않을 때까지 아래로 이동
    while not check_collision(ghost_block):
        ghost_block.y += 1
    ghost_block.y -= 1  # 충돌 직전의 위치로 이동

    return ghost_block

def draw_ghost_block(ghost_block):
    for x, y in ghost_block.get_coords():
        rect = pygame.Rect(
            (grid_x_offset + x) * BLOCK_SIZE,
            y * BLOCK_SIZE,
            BLOCK_SIZE,
            BLOCK_SIZE
        )
        ghost_color = (150, 150, 150)  # 연한 회색
        pygame.draw.rect(screen, ghost_color, rect, 1)  # 테두리만 렌더링


# --- 게임 루프 ---
def game_loop():
    global score, held_block, can_hold, is_paused
    clock = pygame.time.Clock()
    # 블록 생성 부분
    current_block = Block(random.randint(0, len(SHAPES) - 1))
    next_block = Block(random.randint(0, len(SHAPES) - 1))
    game_over = False

    last_move_down_time = pygame.time.get_ticks()
    move_down_interval = 500  # 밀리초 단위 자동 이동 간격

    while True:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()

        # 키 입력 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()  # 음악 중지
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_block.move(-1, 0)
                    if check_collision(current_block):
                        current_block.move(1, 0)
                elif event.key == pygame.K_RIGHT:
                    current_block.move(1, 0)
                    if check_collision(current_block):
                        current_block.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    current_block.move(0, 1)
                    if check_collision(current_block):
                        current_block.move(0, -1)
                        freeze_block(current_block)
                        clear_lines()
                        can_hold = True  # 새 블록이 나오면 홀드 가능 상태 초기화
                        if check_game_over():
                            game_over = True
                        current_block = next_block
                        next_block = Block(random.choice(SHAPES), random.choice(SHAPES_COLORS))
                elif event.key == pygame.K_UP:
                    current_block.rotate()
                    if check_collision(current_block):
                        current_block.rotate()
                        current_block.rotate()
                        current_block.rotate()
                elif event.key == pygame.K_LCTRL:  # 왼쪽 Ctrl 키를 눌렀을 때
                    # 시계 반대 방향으로 -90도 회전
                    current_block.rotate()
                    current_block.rotate()
                    current_block.rotate()
                    if check_collision(current_block):
                        # 원상복구: 시계 방향으로 다시 한 번 회전
                        current_block.rotate()
                elif event.key == pygame.K_LSHIFT:  # 왼쪽 Shift 키로 홀드
                    if can_hold:
                        if held_block is None:
                            held_block = current_block
                            current_block = next_block
                            next_block = Block(random.randint(0, len(SHAPES) - 1))
                        else:
                            held_block, current_block = current_block, held_block
                            current_block.x = GRID_WIDTH // 2 - len(current_block.shape[0]) // 2
                            current_block.y = 0
                        can_hold = False  # 같은 턴에서 다시 홀드할 수 없도록 설정
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    while not check_collision(current_block):
                        current_block.move(0, 1)
                    current_block.move(0, -1)
                    freeze_block(current_block)
                    clear_lines()
                    can_hold = True
                    if check_game_over():
                        game_over = True
                    current_block = next_block
                    next_block = Block(random.randint(0, len(SHAPES) - 1))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC로 일시 정지/재개
                        is_paused = not is_paused  # 일시 정지 상태 변경
        if is_paused:
            draw_pause_message()  # "PAUSED" 메시지 렌더링
            pygame.mixer.music.pause()  # 음악 일시 정지
            pygame.display.flip()  # 화면 업데이트
            clock.tick(60)
            continue  # 일시 정지 상태에서 나머지 작업 건너뜀
        else:
            pygame.mixer.music.unpause()  # 음악 재개

            # 블록 자동 이동
        if current_time - last_move_down_time > move_down_interval:
            current_block.move(0, 1)
            if check_collision(current_block):
                current_block.move(0, -1)
                freeze_block(current_block)
                clear_lines()
                can_hold = True
                if check_game_over():
                    game_over = True
                current_block = next_block
                next_block = Block(random.randint(0, len(SHAPES) - 1))
            last_move_down_time = current_time
        
        if game_over:
            game_over_screen()  # 게임 오버 메시지 표시
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # R키로 게임 재시작
                        pygame.mixer.music.play(-1)  # 무한 반복 재생
                        reset_game()
                        # 블록 생성 부분
                        current_block = Block(random.randint(0, len(SHAPES) - 1))
                        next_block = Block(random.randint(0, len(SHAPES) - 1))
                        game_over = False
                    elif event.key == pygame.K_q:  # Q키로 종료
                        pygame.quit()
                        sys.exit()
            continue  # 게임 오버 상태에서 나머지 작업 건너뜀

        #렌더링
        ghost_block = calculate_ghost_block(current_block)
        draw_ghost_block(ghost_block)
        draw_held_block(held_block)     # 홀드 블록
        draw_grid_with_blocks(current_block)  # 메인 그리드
        draw_next_block(next_block)     # 다음 블록
        draw_score()                    # 점수

        pygame.display.flip()
        clock.tick(60)


# 게임 시작
main()