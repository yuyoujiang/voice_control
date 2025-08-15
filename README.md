# AI电机控制系统

使用大模型function calling功能来控制电机旋转角度的系统。

## 功能特性

- 🤖 **大模型集成**: 支持OpenAI GPT和Ollama本地模型进行自然语言理解和function calling
- 🎯 **精确控制**: 支持精确的电机角度控制（-180°到180°）
- ⚡ **速度控制**: 可调节电机旋转速度（1-100度/秒）
- 🔧 **硬件支持**: 支持实际硬件控制和软件模拟模式
- 📊 **状态监控**: 实时监控电机状态和系统信息
- 🛡️ **安全保护**: 支持紧急停止功能
- 🏠 **本地部署**: 支持Ollama本地模型，无需API密钥

## 系统架构

```
AI电机控制系统
├── 大模型API (OpenAI GPT)
├── Function Calling解析器
├── 电机控制器
│   ├── 软件控制器 (模拟)
│   └── 硬件控制器 (实际)
└── 用户界面
    ├── 命令行界面
    └── Web界面 (可选)
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 选择模型类型

#### 选项A: 使用OpenAI API（需要API密钥）

```bash
# 设置环境变量
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### 选项B: 使用Ollama本地模型（推荐）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载推荐模型
ollama pull qwen2.5:7b-instruct

# 或者使用配置脚本
python setup_ollama.py
```

### 3. 创建日志目录

```bash
mkdir logs
```

## 使用方法

### 1. 使用OpenAI API

```bash
# 软件模式测试
python test_ai_motor_control.py

# 硬件模式测试
python test_ai_motor_control.py --hardware --port COM3
```

### 2. 使用Ollama本地模型（推荐）

```bash
# 软件模式测试
python test_ai_motor_control.py --ollama --model qwen2.5:7b-instruct

# 硬件模式测试
python test_ai_motor_control.py --ollama --model qwen2.5:7b-instruct --hardware --port COM3

# 专门的Ollama测试脚本
python test_ollama_motor_control.py --model qwen2.5:7b-instruct

# 运行function calling测试
python test_ollama_motor_control.py --model qwen2.5:7b-instruct --test
```

### 3. 运行示例

```bash
python example_usage.py
```

## 支持的命令

### 自然语言命令

- "让电机1旋转到90度"
- "将电机2转到-45度，速度30度每秒"
- "停止电机3"
- "查看电机1的状态"
- "紧急停止所有电机"

### 特殊命令

- `status` - 查看所有电机状态
- `info` - 查看系统信息
- `help` - 显示帮助
- `quit` - 退出程序

## 代码示例

### 基本使用

#### 使用OpenAI API

```python
from src.ai_control.ai_motor_controller import AIMotorController

# 初始化控制器
controller = AIMotorController(
    api_key="your-api-key",
    use_hardware=False  # 软件模式
)

# 执行自然语言命令
result = controller.execute_natural_language_command("让电机1旋转到90度")
print(result)
```

#### 使用Ollama本地模型

```python
from src.ai_control.ai_motor_controller import AIMotorController

# 初始化控制器（Ollama模式）
controller = AIMotorController(
    use_ollama=True,
    ollama_model="qwen2.5:7b-instruct",
    ollama_base_url="http://localhost:11434",
    use_hardware=False  # 软件模式
)

# 执行自然语言命令
result = controller.execute_natural_language_command("让电机1旋转到90度")
print(result)
```

### 硬件控制

```python
# 硬件模式
controller = AIMotorController(
    api_key="your-api-key",
    use_hardware=True,
    port="COM3"
)

# 连接硬件
if controller.connect_hardware():
    # 执行命令
    result = controller.execute_natural_language_command("让电机1旋转到45度")
    print(result)
    
    # 断开连接
    controller.disconnect_hardware()
```

### 直接控制

```python
# 直接控制电机
controller.control_motor("motor_1", 60, 40)  # 电机1，60度，40度/秒

# 获取状态
status = controller.get_motor_status("motor_1")

# 停止电机
controller.stop_motor("motor_1")
```

## Function Calling定义

系统定义了以下function calling工具：

### 1. control_motor
控制指定电机的旋转角度和速度

```json
{
  "name": "control_motor",
  "parameters": {
    "motor_id": "string",  // motor_1, motor_2, motor_3
    "angle": "number",     // -180到180度
    "speed": "number"      // 1到100度/秒
  }
}
```

### 2. get_motor_status
获取指定电机的当前状态

```json
{
  "name": "get_motor_status",
  "parameters": {
    "motor_id": "string"  // motor_1, motor_2, motor_3
  }
}
```

### 3. stop_motor
停止指定电机的运动

```json
{
  "name": "stop_motor",
  "parameters": {
    "motor_id": "string"  // motor_1, motor_2, motor_3
  }
}
```

## 硬件通信协议

如果使用硬件模式，系统会通过串口发送以下命令：

- `MOTOR_MOTOR_1_MOVE <angle> <speed>` - 控制电机1
- `MOTOR_MOTOR_2_MOVE <angle> <speed>` - 控制电机2
- `MOTOR_MOTOR_3_MOVE <angle> <speed>` - 控制电机3
- `MOTOR_MOTOR_1_STOP` - 停止电机1
- `MOTOR_MOTOR_2_STOP` - 停止电机2
- `MOTOR_MOTOR_3_STOP` - 停止电机3
- `MOTOR_MOTOR_1_STATUS` - 获取电机1状态
- `MOTOR_MOTOR_2_STATUS` - 获取电机2状态
- `MOTOR_MOTOR_3_STATUS` - 获取电机3状态
- `EMERGENCY_STOP` - 紧急停止所有电机

## 配置文件

系统使用YAML配置文件管理设置：

```yaml
# config/ai_config.yaml
openai:
  api_key: "${OPENAI_API_KEY}"
  api_base: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  timeout: 30

motors:
  motor_1:
    name: "电机1"
    min_angle: -180
    max_angle: 180
    default_speed: 50
    max_speed: 100
```

## 错误处理

系统包含完善的错误处理机制：

- API调用失败处理
- 硬件连接失败处理
- 参数验证
- 超时处理
- 异常恢复

## 日志系统

使用loguru进行结构化日志记录：

- 控制台输出（彩色格式）
- 文件日志（按天轮转）
- 错误追踪
- 性能监控

## 安全注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥
2. **硬件安全**: 使用硬件模式时注意电机安全
3. **紧急停止**: 系统提供紧急停止功能
4. **参数验证**: 所有输入都经过验证

## 扩展功能

可以轻松扩展以下功能：

- 更多电机支持
- 复杂的运动序列
- 传感器集成
- 机器学习优化
- Web界面
- 移动应用

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查环境变量设置
   - 验证API密钥有效性

2. **硬件连接失败**
   - 检查串口端口
   - 验证硬件连接
   - 检查驱动程序

3. **命令解析失败**
   - 检查网络连接
   - 验证API配额
   - 查看日志文件

### 调试模式

```bash
# 启用详细日志
python test_ai_motor_control.py --debug
```

## 推荐的Ollama模型

### 🏆 最佳推荐

1. **Qwen2.5:7B-Instruct** - 中文支持好，function calling能力强
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```

2. **Llama3.1:8B-Instruct** - 通用性强，推理能力好
   ```bash
   ollama pull llama3.1:8b-instruct
   ```

### 🚀 轻量级选择

3. **Mistral:7B-Instruct** - 轻量级，响应速度快
   ```bash
   ollama pull mistral:7b-instruct
   ```

4. **CodeLlama:7B-Instruct** - 代码理解能力强
   ```bash
   ollama pull codellama:7b-instruct
   ```

### 📊 模型对比

| 模型 | 大小 | 中文支持 | Function Calling | 推理速度 | 推荐指数 |
|------|------|----------|------------------|----------|----------|
| Qwen2.5:7B | 7B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Llama3.1:8B | 8B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Mistral:7B | 7B | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| CodeLlama:7B | 7B | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 许可证

本项目采用MIT许可证。 




cd /
sudo ./home/nvidia/Documents/whisper.cpp/build/bin/whisper-server -m /home/nvidia/Documents/whisper.cpp/models/ggml-base.en-q5_0.bin -t 8


cd /
pasuspender sudo ./home/nvidia/Downloads/respeaker/build/wav2text
cd /
pasuspender sudo ./home/nvidia/Downloads/respeaker/build/record_lite




sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up


cd /home/nvidia/whisper_stable/whisper.cpp
./build/bin/whisper-stream -m ./models/ggml-base.en-q5_1.bin -t 8 --step 0 --length 7000 -vth 0.7 --keep 1200


Rotate to 90 degree


