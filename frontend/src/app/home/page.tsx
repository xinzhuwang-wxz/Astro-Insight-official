"use client";
import { useCopilotAction } from "@copilotkit/react-core";
import CalendarSeptember from '@/components/CalendarSeptember'
import { useState } from "react";

export default function HomePage() {
  const [actionStatus, setActionStatus] = useState("待执行");
  const [personName, setPersonName] = useState("未指定");
  
  // 打印注册信息
  console.log("正在注册 sayHello action...");
  
  useCopilotAction({
    name: "sayHello",
    description: "Say hello to someone.",
    parameters: [
      {
        name: "name",
        type: "string",
        description: "name of the person to say greet",
      },
    ],
    handler: async ({ name }) => {
      console.log("执行 sayHello 操作，参数:", name);
      setActionStatus("已执行");
      setPersonName(name || "未指定");
      alert(`Hello, ${name}!`);
      return `成功向${name}问好`;
    },
    render: ({ args, status }) => {
      const name = args?.name ?? "未指定";
      if (status === "inProgress") {
        return <div>准备向 {name} 问好...</div>;
      }
      if (status === "executing") {
        return <div>正在向 {name} 问好...</div>;
      }
      if (status === "complete") {
        return <div>已成功向 {name} 问好</div>;
      }
      return <></>;
    },
  });
  
  console.log("sayHello action 已注册");

  return (
    <div className="min-h-dvh p-6 text-white">
      {/* <div className="mb-4 p-4 bg-white/10 rounded-md">
        <h2 className="text-xl mb-2">Copilot Actions 测试</h2>
        <p>在聊天窗口中尝试以下命令：</p>
        <ul className="list-disc pl-5 mt-2">
          <li>sayHello 张三</li>
          <li>testSayHello</li>
        </ul>
      </div>
      
      <div className="p-4 bg-white/20 rounded-md mt-2">
        <p>操作状态: {actionStatus}</p>
        <p>问候对象: {personName}</p>
      </div> */}
      
      <div className="mt-4">
        <CalendarSeptember />
      </div>
    </div>
  );
}
