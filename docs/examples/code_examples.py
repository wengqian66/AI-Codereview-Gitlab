"""
这个文件包含了各种编程语言的示例代码，用于RAG测试页面的预设示例。
这些示例故意违反了编码规范，用于测试代码审查功能。
"""

# HTML示例：违反规范的导航栏
html_example = '''
<html>
<head>
<title>Bad Navigation</title>
</head>
<body>
    <div id="nav123">
        <div class="NAVBAR">
            <div>
                <a href="">Home</a>
            </div>
            <div onclick="toggle()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div id="NAV_LINKS">
                <div><a href="">About</a></div>
                <div><a href="">Contact</a></div>
                <div><a href="">Services</a></div>
            </div>
        </div>
    </div>
    <img src="logo.jpg">
    <div style="width:1200px;height:500px;background:red;">Content here</div>
</body>
</html>
'''

# CSS示例：违反BEM规范和响应式设计
css_example = '''
#nav123 .NAVBAR {
    width: 1200px !important;
    height: 80px;
    background-color: red;
    position: fixed;
    top: 0px;
    left: 50%;
    margin-left: -600px;
}

.NAVBAR div div div {
    float: left;
    margin-left: 50px;
}

.NAVBAR div div div a {
    color: white;
    font-size: 16px;
    text-decoration: none;
}

.NAVBAR div:nth-child(2) {
    float: right;
    margin-right: 20px;
    cursor: pointer;
}

.NAVBAR div:nth-child(2) span {
    display: block;
    width: 25px;
    height: 3px;
    background: white;
    margin: 5px 0;
}

#NAV_LINKS {
    position: absolute;
    top: 80px;
    left: 0;
    width: 1200px;
    background: red;
    display: none;
}

#NAV_LINKS.show {
    display: block;
}

@media screen and (max-width: 768px) {
    /* 没有移动端适配 */
}
'''

# JavaScript示例：违反ES6+规范和最佳实践
js_example = '''
var navbar;
var navlinks;
var isopen = false;

function init() {
    navbar = document.getElementById('nav123');
    navlinks = document.getElementById('NAV_LINKS');
    
    document.querySelector('.NAVBAR div:nth-child(2)').onclick = function() {
        toggle();
    }
    
    window.onresize = function() {
        resize();
    }
}

function toggle() {
    if (isopen == true) {
        navlinks.className = '';
        isopen = false;
    } else {
        navlinks.className = 'show';
        isopen = true;
    }
}

function resize() {
    if (window.innerWidth > 768) {
        navlinks.className = '';
        isopen = false;
    }
}

window.onload = function() {
    init();
}
'''

# Java示例：违反Java编码规范
java_example = '''
import java.util.*;

public class todoservice {
    public static Map<String, Object> TODOS = new HashMap<>();
    public static int ID = 1;
    
    public static Object createtodo(String title, String desc) {
        Map<String, Object> todo = new HashMap<>();
        todo.put("id", ID++);
        todo.put("title", title);
        todo.put("desc", desc);
        todo.put("status", "todo");
        todo.put("created", new Date().toString());
        
        TODOS.put(String.valueOf(ID), todo);
        return todo;
    }
    
    public static Object gettodo(String id) {
        return TODOS.get(id);
    }
    
    public static List<Object> getalltodos() {
        List<Object> result = new ArrayList<>();
        for(Map.Entry<String, Object> entry : TODOS.entrySet()) {
            result.add(entry.getValue());
        }
        return result;
    }
    
    public static void updatestatus(String id, String status) {
        Object todo = TODOS.get(id);
        if(todo != null) {
            ((Map<String, Object>)todo).put("status", status);
            ((Map<String, Object>)todo).put("updated", new Date().toString());
        }
    }
    
    public static void main(String[] args) {
        createtodo("Test Task", "This is a test");
        System.out.println(getalltodos());
    }
}
'''

# Python示例：违反PEP8和类型注解规范
python_example = '''
import uuid,datetime
from enum import Enum

class taskstatus(Enum):
    TODO="todo"
    DOING="doing"
    DONE="done"

class task:
    def __init__(self,id,title,desc,status,created,updated=None):
        self.id=id
        self.title=title
        self.desc=desc
        self.status=status
        self.created=created
        self.updated=updated

class TaskManager:
    def __init__(self):
        self.tasks={}
    
    def create_task(self,title,desc):
        id=str(uuid.uuid4())
        t=task(id,title,desc,taskstatus.TODO,datetime.datetime.now())
        self.tasks[id]=t
        return t
    
    def get_task(self,id):
        if id in self.tasks:
            return self.tasks[id]
        else:
            return None
    
    def list_tasks(self):
        result=[]
        for k,v in self.tasks.items():
            result.append(v)
        return result
    
    def update_task_status(self,id,status):
        if id in self.tasks:
            self.tasks[id].status=status
            self.tasks[id].updated=datetime.datetime.now()
            return self.tasks[id]
        return None

# 全局变量
manager=TaskManager()

def create(title,desc):
    return manager.create_task(title,desc)

def get(id):
    return manager.get_task(id)
'''

# C++示例：违反C++编码规范
cpp_example = '''
#include <iostream>
#include <string>
#include <map>
#include <vector>
using namespace std;

enum taskstatus {
    TODO,
    DOING, 
    DONE
};

class task {
public:
    string id;
    string title;
    string desc;
    taskstatus status;
    
    task(string i, string t, string d) {
        id = i;
        title = t;
        desc = d;
        status = TODO;
    }
};

class TaskManager {
private:
    map<string, task*> tasks;
    int idcounter;

public:
    TaskManager() {
        idcounter = 1;
    }
    
    task* createTask(string title, string desc) {
        string id = to_string(idcounter++);
        task* t = new task(id, title, desc);
        tasks[id] = t;
        return t;
    }
    
    task* getTask(string id) {
        if(tasks.find(id) != tasks.end()) {
            return tasks[id];
        }
        return NULL;
    }
    
    vector<task*> listTasks() {
        vector<task*> result;
        for(auto it = tasks.begin(); it != tasks.end(); it++) {
            result.push_back(it->second);
        }
        return result;
    }
    
    void updateStatus(string id, taskstatus status) {
        task* t = getTask(id);
        if(t != NULL) {
            t->status = status;
        }
    }
    
    ~TaskManager() {
        for(auto it = tasks.begin(); it != tasks.end(); it++) {
            delete it->second;
        }
    }
};

TaskManager* manager = new TaskManager();

void createTask(string title, string desc) {
    manager->createTask(title, desc);
}
'''

# Go示例：违反Go编码规范和并发安全
go_example = '''
package taskmanager

import (
    "strconv"
    "time"
)

type taskstatus string

const (
    TODO    taskstatus = "todo"
    DOING   taskstatus = "doing" 
    DONE    taskstatus = "done"
)

type task struct {
    Id          string
    title       string
    description string
    Status      taskstatus
    created_at  time.Time
    updated_at  *time.Time
}

type TaskManager struct {
    tasks map[string]*task
    id_counter int
}

var manager *TaskManager

func init() {
    manager = &TaskManager{
        tasks: make(map[string]*task),
        id_counter: 1,
    }
}

func (tm *TaskManager) createTask(title, description string) *task {
    id := strconv.Itoa(tm.id_counter)
    tm.id_counter++
    
    t := &task{
        Id:          id,
        title:       title,
        description: description,
        Status:      TODO,
        created_at:  time.Now(),
    }
    
    tm.tasks[id] = t
    return t
}

func (tm *TaskManager) GetTask(id string) *task {
    if t, ok := tm.tasks[id]; ok {
        return t
    }
    return nil
}

func (tm *TaskManager) ListTasks() []*task {
    var tasks []*task
    for _, task := range tm.tasks {
        tasks = append(tasks, task)
    }
    return tasks
}

func (tm *TaskManager) updateTaskStatus(id string, status taskstatus) *task {
    if task, exists := tm.tasks[id]; exists {
        task.Status = status
        now := time.Now()
        task.updated_at = &now
        return task
    }
    return nil
}

func CreateTask(title, description string) *task {
    return manager.createTask(title, description)
}

func GetTask(id string) *task {
    return manager.GetTask(id)
}
''' 