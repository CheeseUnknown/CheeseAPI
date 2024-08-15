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

若设置后`(self.expired or self.remaining_repetition_num == 0) and self.auto_remove`，则该任务会被立刻删除。

### **`self.auto_remove: bool`**

任务过期后是否自动删除。

若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。

### **`self.active: bool`**

是否激活；未激活将忽略触发信号。

### **`self.inactive: bool`**

【只读】 是否未激活。

### **`self.expected_repetition_num: int | None`**

期望的重复次数。

若设置后`self.remaining_repetition_num == 0 and self.auto_remove`，则该任务会被立刻删除。

### **`self.total_repetition_num: int`**

【只读】 总计的重复次数。

### **`self.remaining_repetition_num: int | None`**

【只读】 剩余的重复次数。

### **`self.unexpired: bool | None`**

【只读】 任务是否未过期。

### **`self.expired: bool | None`**

【只读】 任务是否过期。

### **`self.lastTimer: datetime.datetime | None`**

【只读】 任务上一次的触发时间；`None`代表从未触发过。

### **`self.intervalTime: float`**

最小检查间隔。

### **`self.lastReturn: Any`**

【只读】 上一次的返回值。

### **`self.endTimer: datetime.datetime | None`**

自定义的结束时间。若未设置，则为当前时间。

若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。

### **`def reset(self)`**

重置统计数据，例如`self.total_repetition_num`。
