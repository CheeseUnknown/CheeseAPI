# **Schedule**

## **`class ScheduleTask`**

通过`app.scheduler`可以获取到对应任务的`ScheduleTask`。

一般情况下不会手动实例化该类。

### **`self.key: str`**

【只读】

### **`self.timer: datetime.timedelta`**

任务触发的间隔时间。

### **`self.fn: Callable`**

任务函数。

### **`self.startTimer: datetime.datetime`**

自定义的开始时间。若未设置，则为当前时间。

若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。

### **`self.auto_remove: bool`**

任务过期后是否自动删除。

若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。

### **`self.active: bool`**

是否激活；未激活将忽略触发信号。

### **`self.inactive: bool`**

【只读】 是否未激活。

### **`self.expected_repetition_num: int`**

期望的重复次数；0代表无限次数。

若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。

### **`self.total_repetition_num: int`**

【只读】 总计的重复次数。

### **`self.remaining_repetition_num: int`**

【只读】 剩余的重复次数；-1代表无限次重复。

### **`self.unexpired: bool`**

【只读】 任务是否未过期。

### **`self.expired: bool`**

【只读】 任务是否过期。

### **`self.mode: Literal['multiprocessing', 'threading', 'asyncio']`**

【只读】 运行的模式是进程、线程还是协程。

### **`self.lastTimer: datetime.datetime | None`**

【只读】 任务上一次的触发时间；`None`代表从未触发过。

### **`def reset(self)`**

重置统计数据，例如`self.total_repetition_num`。
