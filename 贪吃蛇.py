"""
贪吃蛇游戏 - 教学版（增强版）
适合Python初学者学习
包含视觉强化和玩法强化功能
作者：教学示例
"""

# ==================== 导入模块 ====================
# 尝试导入pygame库，如果未安装则给出提示
try:
    import pygame
    import random
    import time
    import os
    import sys
except ImportError:
    print("=" * 50)
    print("错误：未检测到pygame库！")
    print("请在命令行中运行以下命令安装：")
    print("    pip install pygame")
    print("=" * 50)
    exit()


# ==================== 字体设置 ====================
def get_font(size):
    """
    获取支持中文的字体
    尝试多个常见中文字体，如果没有则使用系统默认字体
    
    参数：
        size: 字体大小
    
    返回值：
        font: 字体对象
    """
    # Windows常见中文字体路径列表
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
        "C:/Windows/Fonts/simkai.ttf",  # 楷体
        "C:/Windows/Fonts/simfang.ttf", # 仿宋
    ]
    
    # 尝试加载中文字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    # 如果没有找到中文字体，使用系统默认字体（可能显示方框）
    return pygame.font.Font(None, size)


# ==================== 游戏参数设置 ====================
# 窗口大小（单位：像素）
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

# 每个格子的大小（蛇身和食物的大小基准）
GRID_SIZE = 20

# 初始游戏速度（每秒刷新多少帧）
# 数值越小速度越慢，建议范围：3-10
INITIAL_SPEED = 4

# 颜色定义（使用RGB值）
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0)
COLOR_FOOD = (255, 50, 50)

# 蛇头颜色（深绿色）
COLOR_HEAD = (0, 150, 0)

# 方向定义（用坐标变化表示方向）
# 向上：y坐标减少，向下：y坐标增加
# 向左：x坐标减少，向右：x坐标增加
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)


# ==================== 全局变量 ====================
high_score = 0  # 历史最高分（当次运行内）


# ==================== 初始化函数 ====================
def init_game():
    """
    初始化pygame和游戏窗口
    
    返回值：
        screen: 游戏窗口对象，用于后续绘制
        clock: 时钟对象，用于控制游戏速度
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("贪吃蛇 - 教学版")
    clock = pygame.time.Clock()
    return screen, clock


# ==================== 蛇相关函数 ====================
def create_snake():
    """
    创建初始的蛇
    
    返回值：
        snake_body: 蛇身体坐标列表，每个元素是一个[x, y]坐标
        snake_direction: 蛇当前移动方向
    """
    snake_body = [
        [100, 200],
        [80, 200],
        [60, 200]
    ]
    snake_direction = DIRECTION_RIGHT
    return snake_body, snake_direction


def get_snake_color(segment_index, total_length):
    """
    获取蛇身的渐变绿色
    蛇头用深绿色，越靠近尾部颜色越浅
    
    参数：
        segment_index: 当前是第几节蛇身（0是蛇头）
        total_length: 蛇的总长度
    
    返回值：
        (r, g, b): RGB颜色元组
    """
    if segment_index == 0:
        # 蛇头用深绿色
        return COLOR_HEAD
    
    # 计算渐变比例（从1.0到0.3）
    # segment_index越大（越靠近尾部），比例越小，颜色越浅
    ratio = 1.0 - (segment_index / total_length) * 0.7
    
    # 基础绿色值200，根据比例调整
    green = int(200 * ratio)
    # 红色和蓝色稍微加一点，让颜色更柔和
    red = int(20 * (1 - ratio))
    blue = int(20 * (1 - ratio))
    
    return (red, green, blue)


def draw_snake(screen, snake_body):
    """
    绘制蛇到屏幕上，使用渐变绿色
    
    参数：
        screen: 游戏窗口对象
        snake_body: 蛇身体坐标列表
    """
    total_length = len(snake_body)
    
    for i, segment in enumerate(snake_body):
        x = segment[0]
        y = segment[1]
        
        # 获取当前节的颜色
        color = get_snake_color(i, total_length)
        
        # 绘制方块
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect)
        
        # 给蛇身添加边框，让它更有立体感
        border_color = (0, max(0, color[1] - 30), 0)
        pygame.draw.rect(screen, border_color, rect, 1)
    
    # 绘制蛇头细节（眼睛和舌头）
    if len(snake_body) > 0:
        head_x = snake_body[0][0]
        head_y = snake_body[0][1]
        
        # 确定蛇头方向
        if len(snake_body) > 1:
            next_x = snake_body[1][0]
            next_y = snake_body[1][1]
            
            if next_x < head_x:  # 蛇头向右
                direction = 'right'
            elif next_x > head_x:  # 蛇头向左
                direction = 'left'
            elif next_y < head_y:  # 蛇头向下
                direction = 'down'
            else:  # 蛇头向上
                direction = 'up'
        else:
            # 如果蛇只有一个头，默认向右
            direction = 'right'
        
        # 绘制眼睛
        eye_size = GRID_SIZE // 5
        if direction == 'right':
            # 向右：眼睛在头部右侧
            eye1_pos = (head_x + GRID_SIZE - eye_size - 3, head_y + GRID_SIZE // 4)
            eye2_pos = (head_x + GRID_SIZE - eye_size - 3, head_y + GRID_SIZE * 3 // 4 - eye_size)
            # 绘制舌头
            tongue_pos = (head_x + GRID_SIZE + 2, head_y + GRID_SIZE // 2 - 1)
            pygame.draw.line(screen, (255, 100, 100), tongue_pos, (head_x + GRID_SIZE + 8, head_y + GRID_SIZE // 2 - 1), 2)
        elif direction == 'left':
            # 向左：眼睛在头部左侧
            eye1_pos = (head_x + 3, head_y + GRID_SIZE // 4)
            eye2_pos = (head_x + 3, head_y + GRID_SIZE * 3 // 4 - eye_size)
            # 绘制舌头
            tongue_pos = (head_x - 2, head_y + GRID_SIZE // 2 - 1)
            pygame.draw.line(screen, (255, 100, 100), tongue_pos, (head_x - 8, head_y + GRID_SIZE // 2 - 1), 2)
        elif direction == 'up':
            # 向上：眼睛在头部上方
            eye1_pos = (head_x + GRID_SIZE // 4, head_y + 3)
            eye2_pos = (head_x + GRID_SIZE * 3 // 4 - eye_size, head_y + 3)
            # 绘制舌头
            tongue_pos = (head_x + GRID_SIZE // 2 - 1, head_y - 2)
            pygame.draw.line(screen, (255, 100, 100), tongue_pos, (head_x + GRID_SIZE // 2 - 1, head_y - 8), 2)
        else:  # down
            # 向下：眼睛在头部下方
            eye1_pos = (head_x + GRID_SIZE // 4, head_y + GRID_SIZE - eye_size - 3)
            eye2_pos = (head_x + GRID_SIZE * 3 // 4 - eye_size, head_y + GRID_SIZE - eye_size - 3)
            # 绘制舌头
            tongue_pos = (head_x + GRID_SIZE // 2 - 1, head_y + GRID_SIZE + 2)
            pygame.draw.line(screen, (255, 100, 100), tongue_pos, (head_x + GRID_SIZE // 2 - 1, head_y + GRID_SIZE + 8), 2)
        
        # 绘制眼睛
        for eye_pos in [eye1_pos, eye2_pos]:
            # 眼睛白色部分
            pygame.draw.circle(screen, (255, 255, 255), eye_pos, eye_size)
            # 眼睛黑色瞳孔
            pupil_size = eye_size // 2
            pupil_offset = 1 if direction in ['right', 'down'] else -1
            if direction in ['right', 'left']:
                pupil_pos = (eye_pos[0] + pupil_offset, eye_pos[1])
            else:
                pupil_pos = (eye_pos[0], eye_pos[1] + pupil_offset)
            pygame.draw.circle(screen, (0, 0, 0), pupil_pos, pupil_size)


def move_snake(snake_body, direction):
    """
    移动蛇（根据方向更新蛇头位置）
    
    参数：
        snake_body: 蛇身体坐标列表
        direction: 移动方向
    
    返回值：
        new_head: 新蛇头的坐标
    """
    head_x = snake_body[0][0]
    head_y = snake_body[0][1]
    dx = direction[0]
    dy = direction[1]
    new_head_x = head_x + dx * GRID_SIZE
    new_head_y = head_y + dy * GRID_SIZE
    new_head = [new_head_x, new_head_y]
    return new_head


def update_snake_body(snake_body, new_head, ate_food):
    """
    更新蛇身体，实现平滑跟随效果
    
    参数：
        snake_body: 蛇身体坐标列表
        new_head: 新蛇头坐标
        ate_food: 是否吃到食物（决定是否增长）
    
    返回值：
        更新后的蛇身体列表
    """
    # 将新蛇头添加到身体最前面
    snake_body.insert(0, new_head)
    
    # 如果没吃到食物，删除蛇尾（保持长度不变）
    if not ate_food:
        snake_body.pop()
    
    return snake_body


# ==================== 食物相关函数 ====================
def create_food(snake_body):
    """
    随机生成食物位置（确保不在蛇身上）
    
    参数：
        snake_body: 蛇身体坐标列表
    
    返回值：
        food_pos: 食物坐标 [x, y]
    """
    max_x = WINDOW_WIDTH - GRID_SIZE
    max_y = WINDOW_HEIGHT - GRID_SIZE
    
    while True:
        # 随机生成坐标，确保对齐到网格
        food_x = random.randint(0, max_x // GRID_SIZE) * GRID_SIZE
        food_y = random.randint(0, max_y // GRID_SIZE) * GRID_SIZE
        food_pos = [food_x, food_y]
        
        # 检查食物是否在蛇身上
        on_snake = False
        for segment in snake_body:
            if segment[0] == food_x and segment[1] == food_y:
                on_snake = True
                break
        
        # 如果不在蛇身上，就返回这个位置
        if not on_snake:
            break
    
    return food_pos


def draw_food(screen, food_pos):
    """
    绘制食物到屏幕上（红色圆形）
    
    参数：
        screen: 游戏窗口对象
        food_pos: 食物坐标
    """
    center_x = food_pos[0] + GRID_SIZE // 2
    center_y = food_pos[1] + GRID_SIZE // 2
    radius = GRID_SIZE // 2
    
    # 绘制食物主体（红色圆形）
    pygame.draw.circle(screen, COLOR_FOOD, (center_x, center_y), radius)
    # 绘制食物高光（让食物看起来更立体）
    highlight_pos = (center_x - 3, center_y - 3)
    pygame.draw.circle(screen, (255, 150, 150), highlight_pos, radius // 3)


# ==================== 碰撞检测函数 ====================
def check_wall_collision(snake_head):
    """
    检测蛇头是否撞墙
    
    参数：
        snake_head: 蛇头坐标
    
    返回值：
        True: 撞墙了
        False: 没撞墙
    """
    head_x = snake_head[0]
    head_y = snake_head[1]
    
    # 检查是否超出四个边界
    if head_x < 0:
        return True
    if head_x >= WINDOW_WIDTH:
        return True
    if head_y < 0:
        return True
    if head_y >= WINDOW_HEIGHT:
        return True
    
    return False


def check_self_collision(snake_head, snake_body):
    """
    检测蛇头是否撞到自己身体
    
    参数：
        snake_head: 蛇头坐标
        snake_body: 蛇身体坐标列表（不包含新蛇头）
    
    返回值：
        True: 撞到自己了
        False: 没撞到
    """
    for segment in snake_body:
        if snake_head[0] == segment[0] and snake_head[1] == segment[1]:
            return True
    return False


def check_food_collision(snake_head, food_pos):
    """
    检测蛇头是否吃到食物
    
    参数：
        snake_head: 蛇头坐标
        food_pos: 食物坐标
    
    返回值：
        True: 吃到食物了
        False: 没吃到
    """
    # 创建蛇头的矩形
    head_rect = pygame.Rect(snake_head[0], snake_head[1], GRID_SIZE, GRID_SIZE)
    # 创建食物的矩形（食物位置是网格对齐的）
    food_rect = pygame.Rect(food_pos[0], food_pos[1], GRID_SIZE, GRID_SIZE)
    # 检测两个矩形是否相交
    return head_rect.colliderect(food_rect)


# ==================== 方向控制函数 ====================
def get_new_direction(current_direction, key):
    """
    根据按键获取新方向（防止直接反向移动）
    
    参数：
        current_direction: 当前方向
        key: 按下的键
    
    返回值：
        新方向（如果按键无效则返回原方向）
    """
    if key == pygame.K_UP:
        # 如果当前不是向下，就可以向上
        if current_direction != DIRECTION_DOWN:
            return DIRECTION_UP
    elif key == pygame.K_DOWN:
        # 如果当前不是向上，就可以向下
        if current_direction != DIRECTION_UP:
            return DIRECTION_DOWN
    elif key == pygame.K_LEFT:
        # 如果当前不是向右，就可以向左
        if current_direction != DIRECTION_RIGHT:
            return DIRECTION_LEFT
    elif key == pygame.K_RIGHT:
        # 如果当前不是向左，就可以向右
        if current_direction != DIRECTION_LEFT:
            return DIRECTION_RIGHT
    
    # 如果按键无效，保持原方向
    return current_direction


def get_direction_from_scroll(current_direction, scroll_direction):
    """
    根据鼠标滚轮方向获取新方向（防止直接反向移动）
    
    参数：
        current_direction: 当前方向
        scroll_direction: 滚轮方向（'up' 或 'down'）
    
    返回值：
        新方向（如果方向无效则返回原方向）
    """
    # 获取当前方向的名称
    if current_direction == DIRECTION_UP:
        current_name = 'up'
    elif current_direction == DIRECTION_DOWN:
        current_name = 'down'
    elif current_direction == DIRECTION_LEFT:
        current_name = 'left'
    else:
        current_name = 'right'
    
    # 滚轮向上：顺时针转向（上->右->下->左->上）
    # 滚轮向下：逆时针转向（上->左->下->右->上）
    if scroll_direction == 'up':
        # 顺时针转向
        if current_name == 'up':
            return DIRECTION_RIGHT
        elif current_name == 'right':
            return DIRECTION_DOWN
        elif current_name == 'down':
            return DIRECTION_LEFT
        else:  # left
            return DIRECTION_UP
    else:  # scroll_direction == 'down'
        # 逆时针转向
        if current_name == 'up':
            return DIRECTION_LEFT
        elif current_name == 'left':
            return DIRECTION_DOWN
        elif current_name == 'down':
            return DIRECTION_RIGHT
        else:  # right
            return DIRECTION_UP


# ==================== 显示相关函数 ====================
def draw_score(screen, score, length):
    """
    显示当前得分和长度（顶部居中大字）
    
    参数：
        screen: 游戏窗口对象
        score: 当前得分
        length: 当前蛇的长度
    """
    font = get_font(36)  # 使用中文字体
    
    # 显示分数
    score_text = "得分: " + str(score)
    text_surface = font.render(score_text, True, COLOR_WHITE)
    text_x = (WINDOW_WIDTH - text_surface.get_width()) // 2 - 100
    screen.blit(text_surface, (text_x, 10))
    
    # 显示长度
    length_text = "长度: " + str(length)
    length_surface = font.render(length_text, True, COLOR_WHITE)
    length_x = (WINDOW_WIDTH - length_surface.get_width()) // 2 + 100
    screen.blit(length_surface, (length_x, 10))


def draw_countdown(screen, count):
    """
    显示倒计时画面
    
    参数：
        screen: 游戏窗口对象
        count: 剩余秒数
    """
    screen.fill(COLOR_BLACK)
    
    font_big = get_font(100)  # 数字使用中文字体
    font_small = get_font(30)  # 提示文字使用中文字体
    
    # 显示倒计时数字
    count_text = font_big.render(str(count), True, COLOR_WHITE)
    text_x = (WINDOW_WIDTH - count_text.get_width()) // 2
    text_y = (WINDOW_HEIGHT - count_text.get_height()) // 2 - 30
    screen.blit(count_text, (text_x, text_y))
    
    # 显示提示文字
    hint_text = font_small.render("游戏即将开始...", True, COLOR_WHITE)
    hint_x = (WINDOW_WIDTH - hint_text.get_width()) // 2
    hint_y = text_y + 120
    screen.blit(hint_text, (hint_x, hint_y))
    
    pygame.display.flip()


def draw_game_over(screen, score, high_score):
    """
    显示游戏结束画面（包含历史最高分）
    
    参数：
        screen: 游戏窗口对象
        score: 最终得分
        high_score: 历史最高分
    """
    font_big = get_font(60)      # 大标题使用中文字体
    font_medium = get_font(36)   # 中等文字使用中文字体
    font_small = get_font(28)    # 小文字使用中文字体
    
    # 显示"游戏结束"
    game_over_text = font_big.render("游戏结束!", True, COLOR_RED)
    text_x = (WINDOW_WIDTH - game_over_text.get_width()) // 2
    text_y = (WINDOW_HEIGHT - game_over_text.get_height()) // 2 - 80
    screen.blit(game_over_text, (text_x, text_y))
    
    # 显示本次得分
    score_text = font_medium.render("本次得分: " + str(score), True, COLOR_WHITE)
    score_x = (WINDOW_WIDTH - score_text.get_width()) // 2
    score_y = text_y + 80
    screen.blit(score_text, (score_x, score_y))
    
    # 显示历史最高分
    high_score_text = font_medium.render("历史最高: " + str(high_score), True, (255, 215, 0))  # 金色
    high_x = (WINDOW_WIDTH - high_score_text.get_width()) // 2
    high_y = score_y + 50
    screen.blit(high_score_text, (high_x, high_y))
    
    # 显示重新开始提示
    restart_text = font_small.render("按空格键重新开始 或 ESC退出", True, COLOR_WHITE)
    restart_x = (WINDOW_WIDTH - restart_text.get_width()) // 2
    restart_y = high_y + 60
    screen.blit(restart_text, (restart_x, restart_y))


def flash_screen(screen):
    """
    屏幕闪烁白色（吃到食物时的反馈效果）
    
    参数：
        screen: 游戏窗口对象
    """
    # 创建一个白色的半透明覆盖层
    flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    flash_surface.fill(COLOR_WHITE)
    flash_surface.set_alpha(100)  # 设置透明度（0-255）
    
    # 绘制到屏幕上
    screen.blit(flash_surface, (0, 0))
    pygame.display.flip()
    
    # 短暂等待后恢复正常
    pygame.time.wait(50)


# 数值越小速度越慢，建议范围：5-15
INITIAL_SPEED = 6# ==================== 粒子效果类 ====================
class Particle:
    """
    粒子类，用于吃到食物时的爆炸效果
    """
    def __init__(self, x, y, color):
        """
        初始化粒子
        
        参数：
            x: 粒子初始x坐标
            y: 粒子初始y坐标
            color: 粒子颜色
        """
        self.x = x
        self.y = y
        self.color = color
        # 随机速度（向四面八方散开）
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        # 粒子大小
        self.size = random.randint(3, 6)
        # 粒子生命周期
        self.life = 30
        # 初始透明度
        self.alpha = 255
    
    def update(self):
        """
        更新粒子状态
        
        返回值：
            True: 粒子仍然存活
            False: 粒子已死亡
        """
        # 移动粒子
        self.x += self.vx
        self.y += self.vy
        # 添加重力效果
        self.vy += 0.1
        # 减少生命周期
        self.life -= 1
        # 降低透明度
        self.alpha = int(255 * (self.life / 30))
        
        return self.life > 0
    
    def draw(self, screen):
        """
        绘制粒子
        
        参数：
            screen: 游戏窗口对象
        """
        # 创建带透明度的表面
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, self.alpha), 
                          (self.size, self.size), self.size)
        screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


def create_particles(food_pos, num_particles=15):
    """
    在食物位置创建粒子爆炸效果
    
    参数：
        food_pos: 食物坐标 [x, y]
        num_particles: 粒子数量
    
    返回值：
        particles: 粒子列表
    """
    particles = []
    # 食物中心坐标
    center_x = food_pos[0] + GRID_SIZE // 2
    center_y = food_pos[1] + GRID_SIZE // 2
    
    # 定义爆炸颜色（从红色到黄色）
    colors = [
        (255, 50, 50),   # 红色
        (255, 100, 50),  # 橙红色
        (255, 150, 50),  # 橙色
        (255, 200, 50),  # 黄色
        (255, 255, 100), # 亮黄色
    ]
    
    for _ in range(num_particles):
        color = random.choice(colors)
        particle = Particle(center_x, center_y, color)
        particles.append(particle)
    
    return particles


def update_and_draw_particles(screen, particles):
    """
    更新并绘制所有粒子
    
    参数：
        screen: 游戏窗口对象
        particles: 粒子列表
    
    返回值：
        更新后的粒子列表（移除已死亡的粒子）
    """
    new_particles = []
    for particle in particles:
        if particle.update():
            particle.draw(screen)
            new_particles.append(particle)
    return new_particles


# ==================== 游戏速度计算函数 ====================
def get_game_speed(score):
    """
    根据得分计算游戏速度
    每吃5个食物，速度增加1帧
    
    参数：
        score: 当前得分
    
    返回值：
        speed: 当前游戏速度（帧/秒）
    """
    # 基础速度 + 每5分增加1
    speed_increase = score // 5
    current_speed = INITIAL_SPEED + speed_increase
    
    # 限制最大速度为25帧/秒（太快了会很难玩）
    if current_speed > 25:
        current_speed = 25
    
    return current_speed


# ==================== 倒计时函数 ====================
def countdown(screen, clock):
    """
    游戏开始前的3秒倒计时
    
    参数：
        screen: 游戏窗口对象
        clock: 时钟对象
    """
    for i in range(3, 0, -1):
        draw_countdown(screen, i)
        # 等待1秒
        pygame.time.wait(1000)
        
        # 检查是否用户想退出
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
    
    return True


# ==================== 游戏主循环函数 ====================
def game_loop(screen, clock):
    """
    游戏主循环（处理游戏逻辑）
    
    参数：
        screen: 游戏窗口对象
        clock: 时钟对象
    """
    global high_score  # 使用全局变量记录历史最高分
    
    # 初始化游戏状态
    snake_body, snake_direction = create_snake()
    food_pos = create_food(snake_body)
    score = 0
    game_running = True
    game_over = False
    particles = []  # 粒子列表，用于吃到食物时的爆炸效果
    
    # 蛇头摆动效果相关变量
    wiggle_offset = 0  # 摆动偏移量
    wiggle_speed = 0.2  # 摆动速度
    wiggle_amplitude = 2  # 摆动幅度（像素）
    wiggle_direction = 1  # 摆动方向（1 或 -1）
    
    while game_running:
        # ========== 处理事件 ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    # 游戏结束时的按键处理
                    if event.key == pygame.K_SPACE:
                        # 空格键重新开始
                        snake_body, snake_direction = create_snake()
                        food_pos = create_food(snake_body)
                        score = 0
                        game_over = False
                        particles = []  # 清空粒子
                        # 重置蛇头摆动效果
                        wiggle_offset = 0
                        wiggle_direction = 1
                        # 重新开始前倒计时
                        if not countdown(screen, clock):
                            game_running = False
                    
                    elif event.key == pygame.K_ESCAPE:
                        # ESC键退出
                        game_running = False
                
                else:
                    # 游戏进行中的按键处理（方向控制）
                    snake_direction = get_new_direction(snake_direction, event.key)
            
            elif event.type == pygame.MOUSEWHEEL:
                # 鼠标滚轮控制方向
                if not game_over:
                    if event.y > 0:
                        # 滚轮向上滚动：顺时针转向
                        snake_direction = get_direction_from_scroll(snake_direction, 'up')
                    elif event.y < 0:
                        # 滚轮向下滚动：逆时针转向
                        snake_direction = get_direction_from_scroll(snake_direction, 'down')
        
        # ========== 更新游戏状态 ==========
        if not game_over:
            # 更新蛇头摆动效果
            wiggle_offset += wiggle_speed * wiggle_direction
            # 当摆动达到最大幅度时改变方向
            if abs(wiggle_offset) > wiggle_amplitude:
                wiggle_direction *= -1
            
            # 移动蛇
            new_head = move_snake(snake_body, snake_direction)
            
            # 应用摆动效果到蛇头
            # 根据蛇的移动方向，在垂直方向上应用摆动
            if snake_direction in [DIRECTION_RIGHT, DIRECTION_LEFT]:
                # 左右移动时，在Y轴上摆动
                new_head[1] += int(wiggle_offset)
            else:
                # 上下移动时，在X轴上摆动
                new_head[0] += int(wiggle_offset)
            
            # 检测碰撞
            if check_wall_collision(new_head):
                game_over = True
                # 更新历史最高分
                if score > high_score:
                    high_score = score
            
            elif check_self_collision(new_head, snake_body):
                game_over = True
                # 更新历史最高分
                if score > high_score:
                    high_score = score
            
            else:
                # 检测是否吃到食物
                ate_food = check_food_collision(new_head, food_pos)
                
                # 更新蛇身体
                snake_body = update_snake_body(snake_body, new_head, ate_food)
                
                if ate_food:
                    # 得分增加
                    score = score + 1
                    # 创建粒子爆炸效果
                    particles = create_particles(food_pos, num_particles=20)
                    # 生成新食物
                    food_pos = create_food(snake_body)
                    # 屏幕闪烁反馈
                    flash_screen(screen)
        
        # ========== 绘制画面 ==========
        # 清空屏幕（黑色背景）
        screen.fill(COLOR_BLACK)
        
        # 绘制蛇
        draw_snake(screen, snake_body)
        
        # 绘制食物
        draw_food(screen, food_pos)
        
        # 更新并绘制粒子效果
        particles = update_and_draw_particles(screen, particles)
        
        # 显示分数和长度
        draw_score(screen, score, len(snake_body))
        
        # 如果游戏结束，显示结束画面
        if game_over:
            draw_game_over(screen, score, high_score)
        
        # 更新显示
        pygame.display.flip()
        
        # 控制游戏速度（根据得分动态调整）
        current_speed = get_game_speed(score)
        clock.tick(current_speed)


# ==================== 程序入口 ====================
def main():
    """
    主函数：程序的入口点
    """
    global high_score
    high_score = 0  # 初始化历史最高分
    
    # 初始化游戏
    screen, clock = init_game()
    
    # 显示开始倒计时
    if countdown(screen, clock):
        # 开始游戏主循环
        game_loop(screen, clock)
    
    # 退出pygame
    pygame.quit()


# 如果直接运行这个文件，就执行main函数
if __name__ == "__main__":
    main()
