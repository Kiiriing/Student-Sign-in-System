import axios from "axios"

// 动态获取后端地址：使用当前页面的主机 IP + 后端端口 5000
// 这样无论通过 localhost 还是局域网 IP 访问前端，都能正确请求后端
const host = window.location.hostname
const request = axios.create({

    baseURL: `http://${host}:5000`,

    timeout:5000,

    headers:{
        "Content-Type":"application/json"
    }

})

// 请求拦截器：统一附加 JWT
request.interceptors.request.use(
    config => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器：直接透传结果，交由各页面自行处理错误提示
request.interceptors.response.use(
    response => response,
    error => Promise.reject(error)
);

export default request