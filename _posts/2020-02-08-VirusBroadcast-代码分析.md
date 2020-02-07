---
layout:     post
title:      VirusBroadcast 代码分析
subtitle:   "疫情转播仿真程序Java源代码赏析"
date:       2020-02-08
author:     汤泡饭
header-img: img/post-bg-os-metro.jpg
catalog: true
tags:
    - Java
---

# VirusBroadcast 源代码详解
>今天是2019-nCoV新型冠状病毒肺炎爆发、武汉封城的第16天，疫情增长还没有看到专家预言的拐点出现。2月6日**人民日报**公众号转发了一则由Ele实验室制作的疫情转播仿真程序（[*计算机仿真程序告诉你为什么现在不能出门*](http://mp.weixin.qq.com/s/-X1aXiQOwl2HNEi_iiVL5w)），通过调整模型参数，直观地让普通老百姓看到了模拟城市中人群间的交叉感染过程与严重后果。

在作者*Bruce Young*的[GitHub主页](https://github.com/KikiLetGo/VirusBroadcast)上，我download了源代码，发现居然是用Java写的，正好上学期Java考的一言难尽，趁机学习一下大佬的源码。（*半个多月没开过eclipse，它居然就崩了？？正好用学生License注册了一年的InteliJ IDEA，大厂的IDE真香，嗯*）

`VirusBroadcast`项目一共有10个java文件组成，编译运行Main文件后的程序界面如下图所示：

![12WyHU.md.png](https://s2.ax1x.com/2020/02/08/12WyHU.md.png)

接下来，我将按照我认为合理的逻辑顺序分析源代码。

## 1、`Constants.java`
```
public class Constants {
    public static int ORIGINAL_COUNT = 50;//初始感染数量
    public static float BROAD_RATE = 0.8f;//传播率
    public static float SHADOW_TIME = 140;//潜伏时间
    public static int HOSPITAL_RECEIVE_TIME = 10;//医院收治响应时间
    public static int BED_COUNT = 1000;//医院床位
    public static float u = 0.99f;//流动意向平均值
}
```
Constants类中定义了项目的常量参数，如：

`ORIGINAL_COUNT`为初始感染病例、`BROAD_RATE`为病毒的传播率（*正常与被感染病例接触时被感的可能性*）、`SHADOW_TIME`为病毒潜伏时间（*黄点*）、`HOSPITAL_RECEIVE_TIME`为病人确诊到入院隔离的中间时间、`BED_COUNT`为医院床位、`u`为人群的意向流动趋势（*[-1, 1]*）。

## 2、`City.java`
```
public class City {
    private int centerX;
    private int centerY;

    public City(int centerX, int centerY) { //City构造器
        this.centerX = centerX;
        this.centerY = centerY;
    }

    public int getCenterX() {
        return centerX;
    }

    public void setCenterX(int centerX) {
        this.centerX = centerX;
    }

    public int getCenterY() {
        return centerY;
    }

    public void setCenterY(int centerY) {
        this.centerY = centerY;
    }
}
```
City类控制“模拟城市”（*即点的显示区域*）的相关属性。

`centerX`及`centerY`控制人口显示区域的中心位置坐标，后分别有带有参数的类构造器及对X和Y的`get`、`set`方法用来取回参数和设置参数。

## 3、`Point.java`
```
public class Point {
    private int x;
    private int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }

    public int getY() {
        return y;
    }

    public void setY(int y) {
        this.y = y;
    }
}
```
Point类控制人的位置坐标，结构与City类几乎相同，是对坐标点X和Y参数的`get`与`set`，不再赘述。

## 4、`Bed.java`
```
public class Bed extends Point {
    public Bed(int x, int y) {
        super(x, y);
    }

    private boolean isEmpty = true;

    public boolean isEmpty() {
        return isEmpty;
    }

    public void setEmpty(boolean empty) {
        isEmpty = empty;
    }
}
```
Bed类**继承**Point类，子类将继承父类的**非私有的**属性和方法。

子类继承父类时**必须**调用父类的构造器，并且`super`**必须**写在第一行。Bed类中还定义了一个私有boolean类的成员变量`isEmpty`，缺省值为`true`，以及对该变量的判断方法和设置方法。

## 5、`Hospital.java`
```
public class Hospital { 
    private int x = 800;
    private int y = 110;
    private int width;
    private int height = 606;
    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    private static Hospital hospital = new Hospital();

    public static Hospital getInstance() {
        return hospital;
    }

    private Point point = new Point(800, 100);
    private List<Bed> beds = new ArrayList<>();

    private Hospital() {
        if (Constants.BED_COUNT == 0) {
            width = 0;
            height = 0;
        }
        int column = Constants.BED_COUNT / 100;
        width = column * 6;

        for (int i = 0; i < column; i++) {
            for (int j = 10; j <= 610; j += 6) {
                Bed bed = new Bed(point.getX() + i * 6, point.getY() + j);
                beds.add(bed);
            }
        }
    }

    public Bed pickBed() {
        for (Bed bed : beds) {
            if (bed.isEmpty()) {
                return bed;
            }
        }
        return null;
    }
}
```
Hospital类用来控制界面右侧“医院”的绿色矩形图形绘制及相关逻辑。

成员变量`x`和`y`控制矩形框左顶点在面板中的位置坐标，`width`和`height`控制矩形框的宽和高，对应有几个`set`和`get`方法。将Hospital类实例化为变量`hospital`，`getInstance`方法返回该实例。初始化了一个坐标为(800, 100)的Point实例`point`和由Bed类实例构成的链表`beds`。

在Hospital类的构造器中，当床位数为0时，医院矩形框长宽均设为0；绿色矩形框一列可容纳100张床，在后面的代码中我们知道一个点的直径为3像素，因此通过`column`以及后面双重for循环的控制，我们能在绿色矩形框中从上到下、从左至右依次排列确诊病例床位，并保持点与点之间有一定的间距。（*看我画的图*）
![12RjmT.jpg](https://s2.ax1x.com/2020/02/08/12RjmT.jpg)

返回类型为Bed类的方法`pickBed`遍历链表beds，若有空床，则返回该床，否则返回null。

## 6、`PersonPool.java`
```
public class PersonPool {
    private static PersonPool personPool = new PersonPool();

    public static PersonPool getInstance() {
        return personPool;
    }

    List<Person> personList = new ArrayList<Person>();

    public List<Person> getPersonList() {
        return personList;
    }

    private PersonPool() {
        City city = new City(400, 400);
        for (int i = 0; i < 5000; i++) {
            Random random = new Random();
            int x = (int) (100 * random.nextGaussian() + city.getCenterX());
            int y = (int) (100 * random.nextGaussian() + city.getCenterY());
            if (x > 700) {
                x = 700;
            }
            Person person = new Person(city, x, y);
            personList.add(person);
        }
    }
}
```
PersonPool类用**标准正态分布模型**（*Standard Gaussian Distribution*）控制城市中人群分布的初始状态。

首先是类的实例化及实例返回方法，并新建由Person类的实例构成的链表及链表返回方法，后续把所有“人”都保存进来。

PersonPool构造器方法中实例化了一个参数为(400, 400)的城市（*参数(400, 400)为点分布的中心坐标*），用for循环向`personList`中添加5000个居民的坐标点。每个坐标的随机生成规则如下：

* 首先实例化了一个Random类`random`，调用`random.nextGaussian()`方法生成符合标准正态分布的伪随机数，float类型；

* 由《概率论与数理统计》知识可以得到这些随机数均值为0.0，标准差为1.0。同时由正态分布的3σ原则可以得出这些伪随机数分布在(μ-3σ, μ+3σ)区间中的概率为0.9973。
```
(int) (100 * random.nextGaussian() + city.getCenterX())
```
语句通过选择了一个合适的参数**100**，乘上生成的伪随机数来表示点偏移城市中心的距离。（*看我画的图*）

![12Rx7F.jpg](https://s2.ax1x.com/2020/02/08/12Rx7F.jpg)

根据3σ原则容易得出生成的人群点的分布会类似于**H原子的电子云图**：中心密集，边缘稀疏。

![12WsBT.md.png](https://s2.ax1x.com/2020/02/08/12WsBT.md.png)

## 7、`MoveTarget.java`
```
public class MoveTarget {
    private int x;
    private int y;
    private boolean arrived = false;

    public MoveTarget(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }

    public int getY() {
        return y;
    }

    public void setY(int y) {
        this.y = y;
    }

    public boolean isArrived() {
        return arrived;
    }

    public void setArrived(boolean arrived) {
        this.arrived = arrived;
    }
}
```
MoveTarget类同样是对坐标X与Y的相关操作及对应`get`、`set`方法，类中还定义了一个boolean类的成员变量`isArrived`来指示点是否已经移动，缺省值为`false`，以及对该变量的设置方法。

## 8、`Person.java`
Person类是本程序中**最重要**的部分，并且逻辑**非常复杂**！！它控制了点的移动，以及是否被感染等核心问题，我们将代码分段讲解。
### 基本属性
```
    private City city;
    private int x;
    private int y;
    private MoveTarget moveTarget;
    int sig = 1;
    double targetXU;
    double targetYU;
    double targetSig = 50;

    public interface State {
        int NORMAL = 0;
        int SUSPECTED = NORMAL + 1;
        int SHADOW = SUSPECTED + 1;
        int CONFIRMED = SHADOW + 1;
        int FREEZE = CONFIRMED + 1;
        int CURED = FREEZE + 1;
    }
```
Person类中的成员变量有：City类变量`city`、源坐标`x`与`y`、MoveTarget类变量`moveTarget`、源点参数`sig`、目的坐标`targetXU`与`targetYU`、目的点参数`targetSig`。

第一个成员方法为**接口**State，定义了点的当前感染状态。这样做的好处在于使得表示每种状态的常量值在任意时刻都不相同（*1其实没有实际意义*），并且可以通过大于、小于等逻辑判断来把点归入某一类感染状态中（*作者在代码中将其表述为**状态机***）。用后面的代码举例：
```
    public boolean isInfected() {
        return state >= State.SHADOW;
    }

    public void beInfected() {
        state = State.SHADOW;
        infectedTime = MyPanel.worldTime;
    }   
```
`state`变量指示当前点的感染状态（int），如果当前状态大于等于`State.SHADOW`值，通过上面所说的设计思路，“大于等于SHADOW”的状态，有SHADOW、CONFIRMED、FREEZE和CURED，也就是“已被感染状态（*isInfected*）”，就完成了对点的感染状态分类操作。而“正在被感染状态（*beInfected*）”即`state = State.SHADOW`，可判断处于潜伏期。
### 构造器
```
    public Person(City city, int x, int y) {
        this.city = city;
        this.x = x;
        this.y = y;
        targetXU = 100 * new Random().nextGaussian() + x;
        targetYU = 100 * new Random().nextGaussian() + y; 
    }
```

### 辅助方法
```
    public boolean wantMove() {
        double value = sig * new Random().nextGaussian() + Constants.u;
        return value > 0;
    }

    private int state = State.NORMAL;

    public int getState() {
        return state;
    }

    public void setState(int state) {
        this.state = state;
    }

    public int getX() {
        return x;
    }

    public void setX(int x) {
        this.x = x;
    }

    public int getY() {
        return y;
    }

    public void setY(int y) {
        this.y = y;
    }
    
    public double distance(Person person) {
        return Math.sqrt(Math.pow(x - person.getX(), 2) + Math.pow(y - person.getY(), 2));
    }

    private void moveTo(int x, int y) {
        this.x += x;
        this.y += y;
    }
```
* `wantMove`：还记不记得我们在Constants中定义了一个流动意向平均值`u`，其刻画了点移动的**可能性**：如果计算出的value值为正，那么移动，否则不移动。

* `distance`：计算坐标(x, y)与坐标(person.getX(), person.getY())之间的距离。可`x`不就等于`person.getX()`、`y`不就等于`person.getY()`吗？要弄清楚，`x`和`y`是类中的变量，而`person.getX()`和`person.getY()`是类的实例，很有可能不同。

* `moveTo`：改变实例person的坐标位置。

### action方法
```
    private void action() {
        if (state == State.FREEZE) {
            return;
        }
        if (!wantMove()) {
            return;
        }
        if (moveTarget == null || moveTarget.isArrived()) {
            double targetX = targetSig * new Random().nextGaussian() + targetXU;
            double targetY = targetSig * new Random().nextGaussian() + targetYU;
            moveTarget = new MoveTarget((int) targetX, (int) targetY);

        }

        int dX = moveTarget.getX() - x;
        int dY = moveTarget.getY() - y;
        double length = Math.sqrt(Math.pow(dX, 2) + Math.pow(dY, 2));

        if (length < 1) {
            moveTarget.setArrived(true);
            return;
        }
        int udX = (int) (dX / length);
        if (udX == 0 && dX != 0) {
            if (dX > 0) {
                udX = 1;
            } else {
                udX = -1;
            }
        }
        int udY = (int) (dY / length);
        if (udY == 0 && udY != 0) {
            if (dY > 0) {
                udY = 1;
            } else {
                udY = -1;
            }
        }

        if (x > 700) {
            moveTarget = null;
            if (udX > 0) {
                udX = -udX;
            }
        }
        moveTo(udX, udY);
    }
```
`action`方法控制点的**一次移动**。

* 当点的状态为FREEZE或者`wantMove`值为`false`时，return。
* 当目标点不存在或者因为其他原因认定已经移动到目标点时，重新用高斯分布伪随机数计算目标点坐标并set。

那么在什么情况下会认定已经移动到目标点呢？计算源点与目标点的距离，当距离小于1像素时，认为已经移动到目标点，重新计算目标。

当目标点坐标有效时，直接移到目标坐标点吗？距离太大了是不是有点违背常识？因此，当目标点坐标有效时，源点的移动规则是：以源点为中心建立平面直角坐标系，目标点落入哪个象限内，就向那个象限的正方向角平分线移动根号2个像素点。（*看我画的图*）

![12Rv0U.md.jpg](https://s2.ax1x.com/2020/02/08/12Rv0U.md.jpg)

### update方法
```
public void update() {
        if (state >= State.FREEZE) {
            return;
        }
        if (state == State.CONFIRMED && MyPanel.worldTime - confirmedTime >= Constants.HOSPITAL_RECEIVE_TIME) {
            Bed bed = Hospital.getInstance().pickBed();
            if (bed == null) {
                System.out.println("隔离区没有空床位");
            } else {
                state = State.FREEZE;
                x = bed.getX();
                y = bed.getY();
                bed.setEmpty(false);
            }
        }
        if (MyPanel.worldTime - infectedTime > Constants.SHADOW_TIME && state == State.SHADOW) {
            state = State.CONFIRMED;
            confirmedTime = MyPanel.worldTime;
        }

        action();

        List<Person> people = PersonPool.getInstance().personList;
        if (state >= State.SHADOW) {
            return;
        }
        for (Person person : people) {
            if (person.getState() == State.NORMAL) {
                continue;
            }
            float random = new Random().nextFloat();
            if (random < Constants.BROAD_RATE && distance(person) < SAFE_DIST) {
                this.beInfected();
            }
        }
    }
```
`update`方法更新**一次**点的移动状态（*包括位置及感染状态*）。

* 当目前点状态为CONFIRMED并且当前距离确诊时间已超过医院收治响应时间时（*也就是说已经进医院被隔离*），对bed进行获取床位操作：剩余床位已空时print床位不足提示；还有床位时获取“床位点”坐标，占领床位，并将点送入医院隔离区。

* 当点处于潜伏状态且目前时刻与被感染时刻之差超过潜伏期时，状态变更为CONFIRMED，并更新确诊时间。

* 调用`action`方法，完成一次点的移动。

* 在当前点状态未被感染时对people链表中的所有点进行遍历：寻找到**当前时刻**每一个被感染的点坐标，计算这个点与当前点的距离，若小于安全距离则当前点被感染。（*注意还有一个传播率的限制*）

### 总结Person类
`update`方法和`action`方法配合起来：
* 针对**当前时刻**的所有点计算了下一帧的移动目标点并移动；

* 将已确诊点送入医院隔离；

* 针对**当前时刻**的所有已感染点（*含潜伏与确诊*）继续对其周围小于安全距离的正常点进行感染。

完成动作后保存所有点状态，待下一帧刷新时将所有点绘制在画面上。

## 9、`MyPanel.java`
```
public class MyPanel extends JPanel implements Runnable {
    private int pIndex = 0;

    public MyPanel() {
        this.setBackground(new Color(0x444444));
    }

    @Override
    public void paint(Graphics arg0) {
        super.paint(arg0);
        //draw border
        arg0.setColor(new Color(0x00ff00)); 
        arg0.drawRect(Hospital.getInstance().getX(), Hospital.getInstance().getY(),
                Hospital.getInstance().getWidth(), Hospital.getInstance().getHeight());

        List<Person> people = PersonPool.getInstance().getPersonList();
        if (people == null) {
            return;
        }
        people.get(pIndex).update();
        for (Person person : people) {
            switch (person.getState()) {
                case Person.State.NORMAL: {
                    arg0.setColor(new Color(0xdddddd));
                }
                break;
                case Person.State.SHADOW: {
                    arg0.setColor(new Color(0xffee00));
                }
                break;
                case Person.State.CONFIRMED:
                case Person.State.FREEZE: {
                    arg0.setColor(new Color(0xff0000));
                }
                break;
            }
            person.update();
            arg0.fillOval(person.getX(), person.getY(), 3, 3); 
        }
        pIndex++;
        if (pIndex >= people.size()) {
            pIndex = 0;
        }
    }

    public static int worldTime = 0;

    @Override
    public void run() {
        while (true) {
            this.repaint();
            try {
                Thread.sleep(100);
                worldTime++;
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
```
MyPanel类用来控制GUI图形界面，**继承**JPanel类并实现Runnable接口进行多线程操作。

`pIndex`变量获取链表中对应索引的Person对象；MyPanel构造器初始化窗口背景颜色；**重写**的`paint`方法依次绘制医院绿色矩形边框、初始化PersonPool后遍历people链表中的每一个点，按不同的感染状态设置绘制颜色，调用`update`方法完成所有点的信息更新，调用`fillOval`方法绘制圆点（*参数说明：前两个参数为椭圆外接矩形的左上顶点坐标，后两个参数为椭圆外接矩形的宽与高*）。遍历结束后，`pIndex`值归零。**重写**的`run`方法在线程暂停100ms后重绘界面，也就是说刷新间隔为100ms。

## 10、`Main.java`
```
public class Main {
    public static void main(String[] args) {
        MyPanel p = new MyPanel();
        Thread panelThread = new Thread(p);
        JFrame frame = new JFrame();
        frame.add(p);
        frame.setSize(1000, 800);
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        panelThread.start();

        List<Person> people = PersonPool.getInstance().getPersonList();
        for (int i = 0; i < Constants.ORIGINAL_COUNT; i++) {
            int index = new Random().nextInt(people.size() - 1);
            Person person = people.get(index);

            while (person.isInfected()) {
                index = new Random().nextInt(people.size() - 1);
                person = people.get(index);
            }
            person.beInfected();
        }
    }
}
```
前面9项代码都搞懂了，Main不用我再多解释了吧。里面的循环就是对参数中设置的初始感染人数进行遍历，初始化这些人“被感染进入潜伏期”。

## 11、总结
其实这个项目最难理解的地方在Person.java中，**重点**是理解怎样确定点移动后的位置、以何种规则来移动点、如何描述“碰到会感染”的逻辑、以什么方式来分辨点的感染状态。作者说他用了一个整晚上写完了所有代码，在仔细理解所有细节后我觉得作者的思路很棒，写的也非常好。当然这个模拟模型也有值得**商榷和改进**的地方，如人群的分布模型、流动意向和单中心辐射城市的结构，但作为科普类项目，已足以直观地解释和说明。

我对代码的分析和理解肯定有错误和疏漏之处，欢迎和我一起探讨。我觉得Java作为一门OOP语言在这样的项目编程中有其他语言难以比拟的优越性（当然Python或者MatLab在模型分析拟合上还是十分强大，在这里我只是探讨语言本身，什么数学模型统计之类的交给数学学院的同学吧），还要认真学习。

这是我第一次对别人写的代码进行完整的文字分析（还是第一次用Markdown写这么长，比起Word来说真香），以前都是在实验报告里对自己的东西分析,分析别人的代码其实是很痛苦的，尤其是这种几乎**没有注释**的代码（提醒我们要养成良好的编码习惯），所以分析代码时你要去猜、根据变量和方法的命名来推测它可能的功能；注意代码的结构，当代码很长、在一屏上显示不完全时，要善于借助IDE的功能，提出代码结构，便于分析。

今天居然都正月十五了，这个特殊的春节虽说无聊但过得还是挺快的。希望疫情早日解除，我真想回学校上课了。

就这样，晚安！

2020/02/08    01:00
