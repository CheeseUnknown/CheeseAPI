# **Demo**

每个demo中的`app.py`有一行代码`app.workspace.base = os.path.dirname(os.path.abspath(__file__))`，它用于在CheeseAPI中启动时使用本地的CheeseAPI，

## **在CheeseAPI中启动**

```
git clone https://github.com/CheeseUnknown/CheeseAPI
cd CheeseAPI
python ./demo/<某个demo>/.py
```

若工作区不在CheeseAPI目录，会有引用错误

## **单个demo项目启动**

```
pip install CheeseAPI
cd <某个demo>
python app.py
```
