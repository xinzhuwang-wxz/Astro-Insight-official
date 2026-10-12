import { redirect } from "next/navigation";

export default function SerialPage() {
	// 串口功能已移除，直接跳转到首页
	redirect("/home");
}
