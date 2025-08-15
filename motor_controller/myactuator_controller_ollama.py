
from llm.ollama_motor_controller import OllamaMotorController
import myactuator_rmd_py as rmd
import time
from loguru import logger
from typing import Dict, List, Optional, Any


class MyActuatorControllerOllama(OllamaMotorController):
    """MyActuator电机控制器，继承自OllamaMotorController"""
    
    def __init__(self, model: str, base_url: str = "http://localhost:11434", port: str = "can0"):
        super().__init__(model, base_url)

        self.driver = rmd.CanDriver(port)
        self.motors = {
            "motor_1": rmd.ActuatorInterface(self.driver, 1),
            "motor_2": rmd.ActuatorInterface(self.driver, 2),
            "motor_3": rmd.ActuatorInterface(self.driver, 3)
        }

    def control_motor(self, motor_id: str, angle: float, speed: float = 300) -> dict[str, any]:
        """控制电机旋转到指定角度"""
        if motor_id not in self.motors:
            return {"success": False, "error": f"无效的电机ID: {motor_id}"}
        if not 1 <= speed <= 800:
            return {"success": False, "error": "速度必须在1到800度/秒之间"}

        logger.info(f"控制电机 {motor_id} 旋转到 {angle}度，速度 {speed}度/秒")
        motor_id = "motor_1"
        self.motors[motor_id].sendPositionAbsoluteSetpoint(-angle, speed)
        # time.sleep(3)  # Wait for motor to reach target position

        return {
            "success": True,
            "motor_id": motor_id,
            "target_angle": angle,
            "speed": speed,
            "message": f"电机 {motor_id} 开始旋转到 {angle}度"
        }

    def get_motor_status(self, motor_id: str) -> Dict[str, Any]:
        """获取电机状态"""

        def _get_motor_status(actuator):
            status1 = actuator.getMotorStatus1()
            status2 = actuator.getMotorStatus2()
            status3 = actuator.getMotorStatus3()
            status_str = f"""
                Motor Status 1:
                Temperature: {status1.temperature}°C
                Brake Status: {'Released' if status1.is_brake_released else 'Locked'}
                Voltage: {status1.voltage}V
                Error Code: {status1.error_code}

                Motor Status 2:
                Temperature: {status2.temperature}°C
                Current: {status2.current}A
                Shaft Speed: {status2.shaft_speed} RPM
                Shaft Angle: {status2.shaft_angle}°

                Motor Status 3:
                Temperature: {status3.temperature}°C
                Phase A Current: {status3.current_phase_a}A
                Phase B Current: {status3.current_phase_b}A
                Phase C Current: {status3.current_phase_c}A
                """
            return status_str

        if motor_id not in self.motors:
            return {"success": False, "error": f"无效的电机ID: {motor_id}"}
        
        return {
            "success": True,
            "motor_id": motor_id,
            "status": _get_motor_status(self.motors[motor_id])
        }

    def stop_motor(self, motor_id: str) -> Dict[str, Any]:
        """停止电机运动"""
        if motor_id not in self.motors:
            return {"success": False, "error": f"无效的电机ID: {motor_id}"}

        self.motors[motor_id].stopMotor()
        logger.info(f"停止电机 {motor_id}")
        
        return {
            "success": True,
            "motor_id": motor_id,
            "message": f"电机 {motor_id} 已停止"
        }
