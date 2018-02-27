# 1.帧头数据
```
typedef __packed struct
{
  uint32_t  irm;           /* 域ID, 主控和裁判系统域：0xA5；主控和PC上层域：0xA0 */
  uint16_t data_length;   /* 每帧内数据data的长度 */
  uint8_t  crc8;          /* 帧头的crc校验结果 */
} frame_header_t;
```

帧头数据			|占用字节				| 详细描述|
----------------|-------------------|-----------------------|
irm					|    4   					| 数据的域ID，主控和裁判系统域：0xA5；主控和PC上层域：0xA0|
data_length		| 2						|每帧内数据data的长度|
crc8				|1						|帧头的crc校验结果|

*备注：*

>数据的域 ID 主要分为上层域 0xA0 和底层域 0xA5。
>
>0xA5 域为裁判系统和机器人主控的通信域 ID ，主要是裁判系统的比赛信息数据和用户自定义数据上传。
>
>0xA0 域的数据为上层 PC 和主控的通信数据，主要包括 PC 对底层的控制数据和底层的反馈数据，以及主控转发给上层的裁判系统数据


# 2.命令码

一个命令码对应一帧包含具体信息的数据，下面是现有所有数据对应的命令码。

命令码				|占用字节				|
-----------------|-------------------|
cmdid				|2						|

```
typedef enum              /* 命令码, cmdid, 2bytes */
{
  GAME_INFO_ID        = 0x0001,     /* 比赛进程 */
  REAL_FIELD_DATA_ID  = 0x0005,     /* 场地交互 */     
  GAIN_BUFF_ID        = 0x0007,     /* 获取buff */
  
  SHOOT_TASK_DATA_ID  = 0x0012,     /* 发射机构 */
  
  CHASSIS_CTRL_ID     = 0x00A0,     /* 底盘控制 */
  GIMBAL_CTRL_ID      = 0x00A1,     /* 云台控制 */
  SHOOT_CTRL_ID       = 0x00A2,     /* 发射机构控制 */
  ERROR_LEVEL_ID      = 0x00A3,     /* 全局错误 */
  CALI_GIMBAL_ID      = 0x00A5,     /* 云台校准 */
  
  STU_CUSTOM_DATA_ID  = 0x0100,     /* 客户端显示 */
  CLIENT_TO_ROBOT_ID  = 0x0102,     /* 转发到决策PC */

  SHO_MOD_SWI_ID      = 0x0700,     /* 设计模式切换 */
  TACT_CMD_ID         = 0x0701,     /* 战术指令 */
  HERO_BULLET_ID      = 0x0702,     /* 英雄取弹 */
  ACKNOWLEDGE_ID      = 0x0703,     /* acknowledge */
} command_id_e;
```

命令码对应的数据传输方向和具体功能如下：


|命令码				|传输方向				|功能介绍       |频率 |
|-----------------|-------------------|-------------|-----|
|0x0001				|主控-->PC   			|比赛时机器人状态|待定|
|0x0005				|主控-->PC   			|场地交互数据    |待定|
|0x0007				|主控-->PC   			|获得buff数据   |待定|
|					|						|	           |    |
| 0x0012 | 主控-->PC | 机器人射击任务信息        |待定        |
|        |         |                  |                |
| 0x00A0 | PC-->主控 | 云台控制信息           |待定         |
| 0x00A1 | PC-->主控 | 底盘控制信息           |待定         |
| 0x00A2 | PC-->主控 | 发射机构控制信息         |待定         |
| 0x00A3 | PC-->主控 | 电脑端运行错误警告级别      |待定         |
| 0x00A5 | PC-->主控 | 云台相关校准信息         |待定      |
|        |         |                  |                |
| 0x0100 | PC-->主控 | PC 需要转发到客户端显示的数据 | 待定         |
| 0x0102 | 主控-->PC | 客户端给 PC 的数据      | 待定         |
|        |         |                  |                |
| 0x0700 |           | 射击模式切换 | 待定         |
| 0x0701 |           | 战术指令   | 待定         |
| 0x0702 |           | 英雄取弹      | 待定        |
| 0x0703 |			 |acknowledge		| 待定       |


# 3.数据  

为命令码 ID 对应的数据结构，数据长度即这个结构体的大小。

| 数据   | 占用字节        |
| :--- | :---------- |
| data | data_length |

## 第一类

### 0x0001 比赛进程 

对应数据结构 `game_info_t`，比赛进程信息

```
typedef __packed struct     /* 0x0001 比赛进程 */
{                           /* 对应数据结构 game_info_t，比赛进程信息 */
  uint16_t   stage_remain_time;     /* 当前阶段剩余时间，单位 s */
  uint8_t    game_process;
  /* current race stage
     0 not start
     1 preparation stage
     2 self-check stage
     3 5 seconds count down
     4 fighting stage
     5 result computing stage */
  uint8_t    reserved;
  uint16_t   remain_hp;
  uint16_t   max_hp;
  position_t position;
} game_robot_state_t;
```

| 数据                | 说明            |
| ---------------- | ------------- |
| `stage_remain_time` | 当前阶段剩余时间，单位 s |
| game_process      | 当前比赛阶段        |
|                   | 0: 未开始比赛      |
|                   | 1: 准备阶段       |
|                   | 2: 自检阶段       |
|                   | 3: 5s 倒计时     |
|                   | 4: 对战中        |
|                   | 5: 比赛结算中      |
| reserved          | 保留位           |
| remain_hp         | 机器人当前血量       |
| max_hp            | 机器人满血量        |
| position          | 位置、角度信息       |

*备注：*

>位置、角度控制信息包含在 `position_t` 结构体中：

```
typedef __packed struct
{
  uint8_t valid_flag;	/* 位置、角度信息有效标志位 */
  float x;
  float y;
  float z;
  float yaw;
} position_t;
```

| 数据         | 说明           |
| ---------- | ------------ |
| valid_flag | 位置、角度信息有效标志位 |
|            | 0: 无效        |
|            | 1: 有效        |
| x          | 位置 X 坐标值     |
| y          | 位置 Y 坐标值     |
| z          | 位置 Z 坐标值     |
| yaw        | 枪口朝向角度值      |


### 0x0005 场地交互

对应数据结构 `rfid_detect_t`，场地交互数据

```
typedef __packed struct
{
  uint8_t region_idx;
} rfid_detect_t;
```

| 数据        | 说明             |
| --------- | -------------- |
| region_idx  | 索引号，用于区分不同区域 |

### 0x0007 获取buff 

对应数据结构 `get_buff_t`，获取到的Buff数据

```
typedef __packed struct
{
  uint8_t buff_type;
  uint8_t buff_addition;
} get_buff_t;
```

| 数据            | 说明      |
| ------------- | ------- |
| buff_type     | Buff类型  |
|               | 0: 攻击加成 |
|               | 1: 防御加成 |
| buff_addition | 加成百分比   |

## 第二类

### 0x0012 发射机构

对应数据结构 `shoot_info_t`，发射机构状态信息

```
typedef __packed struct
{
  int16_t remain_bullets;  /* the member of remain bullets */
  int16_t shot_bullets;    /* the member of bullets that have been shot */
  uint8_t fric_wheel_run; /* friction run or not */
} shoot_info_t;
```

### 0x0013 底层错误
对应数据结构 `infantry_err_t`，底层步兵错误信息

```
typedef __packed struct
{
  bottom_err_e err_sta;                 /* bottom error state */
  bottom_err_e err[ERROR_LIST_LENGTH];  /* device error list */
} infantry_err_t;
```

| 数据                     | 说明          |
| ---------------------- | ----------- |
| err_sta                | 底层设备全局状态    |
| err[ERROR_LIST_LENGTH] | 所有设备、机构工作状态 |

*备注：*

底层错误信息的枚举类型 bottom_err_e 如下，如果相应设备出现错误，状态位被置为`ERROR_EXIST`

```
typedef enum
{
  DEVICE_NORMAL = 0,
  ERROR_EXIST   = 1,
  UNKNOWN_STATE = 2,
} bottom_err_e;
```

底层错误信息的所有分类包含在 err_id_e 中，主要分 3 类。第一类是 `设备_OFFLINE` 相关的设备离线；第二类是机构运行故障，目前只有卡弹这一项；第三类是 `_CONFIG_ERR` 软件相关的配置出现错误，如配置的云台安装位置超出了底盘的物理范围等。

```
typedef enum
{
  BOTTOM_DEVICE        = 0,
  GIMBAL_GYRO_OFFLINE  = 1,
  CHASSIS_GYRO_OFFLINE = 2,
  CHASSIS_M1_OFFLINE   = 3,
  CHASSIS_M2_OFFLINE   = 4,
  CHASSIS_M3_OFFLINE   = 5,
  CHASSIS_M4_OFFLINE   = 6,
  REMOTE_CTRL_OFFLINE  = 7,
  JUDGE_SYS_OFFLINE    = 8,
  GIMBAL_YAW_OFFLINE   = 9,
  GIMBAL_PIT_OFFLINE   = 10,
  TRIGGER_MOTO_OFFLINE = 11,
  BULLET_JAM           = 12,
  CHASSIS_CONFIG_ERR   = 13,
  GIMBAL_CONFIG_ERR    = 14,
  ERROR_LIST_LENGTH    = 15,
} err_id_e;
```


## 第三类

### 0x00A0 底盘控制 

对应数据结构 `chassis_ctrl_t`，底盘控制信息

```
underconstruction
```


### 0x00A1 云台控制 

对应数据结构 `gimbal_ctrl_t`，云台控制信息

```
typedef __packed struct
{
  float   pit_ref;      /* gimbal pitch reference angle(degree) */
  float   yaw_ref;      /* gimbal yaw reference angle(degree) */
} gimbal_ctrl_t;
```

| 数据           | 说明                        |
| ------------ | ------------------------- |
| pit_ref      | pitch 轴相对于中点的目标角度         |
| yaw_ref      | yaw 轴相对于中点的目标角度           |

### 0x00A2 发射机构控制 

对应数据结构 `shoot_ctrl_t`，发射机构控制信息

```
underconstruction
```


### 0x00A3 全局错误

对应数据结构 `global_err_level_t`，整个系统的运行警告级别

```
typedef __packed struct
{
  err_level_e err_level;  /* the error level is included in err_level_e enumeration */
} global_err_level_t;
```

| 数据        | 说明                      |
| --------- | ----------------------- |
| err_level | 主要参见 err_level_e 类型中的数据 |

*备注：*

>整个系统的运行警告级别包含在 `err_level_e` 枚举类型中：

```
typedef enum
{
  GLOBAL_NORMAL        = 0,
  SOFTWARE_WARNING     = 1,
  SOFTWARE_ERROR       = 2,
  SOFTWARE_FATAL_ERROR = 3,
  SHOOT_ERROR          = 4,
  CHASSIS_ERROR        = 5,
  GIMBAL_ERROR         = 6,
} err_level_e;
```

上面的信息可以理解为按照优先级或者紧急程度排序，数字越大代表优先级、紧急程度越高。

*备注：*

> 系统的错误级别由上层发送给底层，如果出现多种类型错误，发送时会选择最高优先级的发送。错误级别数据可以分为两类：一类是上层软件的运行情况，第二类是底层硬件出现的错误。用户可以自定义出现这些不同级别的错误时的处理，目前的处理方式为，软件层的状态除了 `SOFTWARE_FATAL_ERROR`，其他的情况底层都不会做出响应，底层收到出现 `SOFTWARE_FATAL_ERROR` 的信息后，会切断云台和底盘的输出。第二类硬件的错误，主要由底层数据 err_id_e 中包含的数据错误列表分类得出，如果是哪个机构出现了问题，则它自己以及比它优先级低的设备都会切断输出。

### 0x00A5 云台校准

对应数据结构 `cali_cmd_t`，云台校准指令信息

```
underconstruction
```

## 第四类

### 0x0100 客户端显示

对应数据结构 `client_show_data_t`，自定义数据

```
typedef __packed struct
{
  float data1;
  float data2;
  float data3;
  ......(underconstruction)
} client_show_data_t;
```

| 数据    | 说明     |
| ----- | ------ |
| data1 | 自定义数据1 |
| data2 | 自定义数据2 |
| data3 | 自定义数据3 |
|......(underconstruction)|......(underconstruction)|

### 0x0102 转发到决策 PC

对应数据结构 `server_to_user_t`，透传下行数据

```
typedef __packed struct
{
  uint8_t data[32];
  ......(underconstruction)
} server_to_user_t;
```

| 数据       | 说明          |
| -------- | ----------- |
| data[32] | 自定义数据，最大为32 |
|......(underconstruction)|......(underconstruction)|


## 第五类

### 0x0700 射击模式切换
对应数据结构 `shoot_mod_swi_t`，射击模式切换信息

```
underconstruction
```


### 0x0701 战术指令信息
对应数据结构 `tactical_cmd_t`，战术指令信息

```
underconstruction
```


### 0x0702 英雄取弹信息
对应数据结构 `hero_getbullet_t`，英雄取弹信息

```
underconstruction
```


### 0x0703 acknowledge
对应数据结构 `acknowledgement_t`，acknowledgment

```
underconstruction
```