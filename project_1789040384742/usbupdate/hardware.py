"""AutoCar hardware adapter; import/construct AT only when hardware is requested."""
import time


def successful(result, action):
    if isinstance(result, dict):
        ok = result.get('success', False)
    else:
        ok = getattr(result, 'success', result)
    if not ok:
        raise RuntimeError(action + '失败或未返回可确认的成功结果')
    return result


class AutoCarHardware:
    def __init__(self, config, event, at=None):
        self.config = config
        self.event = event
        if at is None:
            try:
                from autocar import AT
            except ImportError as exc:
                raise RuntimeError('请使用已安装 AutoCar 的 Python 运行脚本（AUTOCAR_PYTHON）') from exc
            at = AT()
        self.at = at

    def switch_usb(self, destination):
        config = self.config['usb_switch']
        if destination not in ('pc', 'car'):
            raise RuntimeError('USB 目标只能是 pc 或 car')
        channels = [config.get('pc_usb_port'), config.get('car_usb_port')]
        if any(type(x) is not int or x not in range(1, 5) for x in channels) or channels[0] == channels[1]:
            raise RuntimeError('请按实际接线配置不同的 pc_usb_port/car_usb_port（1～4）')
        channel = config[destination + '_usb_port']
        self.event('USB_SWITCH_REQUESTED', destination=destination, port=config['port'], channel=channel)
        print(f"USB 切换：{config['port']} → {destination}（USB{channel}）", flush=True)
        result = successful(self.at.usb_switch(port=config['port'], usb_port=channel), 'USB 切换')
        # SDK versions may return a MethodResult wrapper or a dictionary.
        # The installed registry documents MethodResult["response_port"].
        try:
            response_port = result['response_port']
        except (KeyError, TypeError) as exc:
            raise RuntimeError('USB 切换结果缺少 response_port 回读') from exc
        if response_port != channel:
            raise RuntimeError(f'USB 切换器回读通道不匹配：请求 USB{channel}，回读 {response_port!r}')
        self.event('USB_SWITCHED', destination=destination, port=config['port'], channel=channel, response_port=response_port)
        print(f'切换器回读成功：USB{response_port}；接下来检查目标端设备枚举。', flush=True)

    def power_cycle(self):
        config = self.config['power']
        delay = config['off_seconds']
        if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not 0 < delay <= 300:
            raise RuntimeError('off_seconds 必须在 0～300 秒之间且大于 0')
        ps = self.at.power_open(config['resource'])
        if ps is None:
            raise RuntimeError('未获得程控电源对象')
        self.event('POWER_OFF_REQUESTED', resource=config['resource'])
        successful(ps.set_output(on=False), '程控电源下电')
        self.event('POWER_OFF_CONFIRMED')
        # Do not put power-on in finally: cancellation must not trigger hidden actions.
        time.sleep(delay)
        successful(ps.set_output(on=True), '程控电源上电')
        self.event('POWER_ON_CONFIRMED')
