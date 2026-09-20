import {createRouter,createWebHistory} from "vue-router"

// 路由组件全部改为按需加载（懒加载）：
// 登录页不再连带下载学生/教师/管理员的整包代码，
// 只有真正进入对应角色页面时才拉取对应的 chunk。
const router=createRouter({

history:createWebHistory(),

routes:[

{
path:"/",
redirect:"/login"
},

{
path:"/login",
component:()=>import("../views/Login.vue")
},

{
path:"/student/dashboard",
component:()=>import("../views/StudentDashboard.vue")
},

{
path:"/teacher/dashboard",
component:()=>import("../views/teacherDashboard.vue")
},

{
path:"/admin/dashboard",
component:()=>import("../views/AdminDashboard.vue")
},

]

})

export default router