export interface Student {


    uuid:string;


    student_no:string;


    name:string;


    class_name:string;


}



export interface LoginResult {


    code:number;


    msg:string;


    data:Student;


}