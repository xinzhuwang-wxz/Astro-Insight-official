"use client";

import {useEffect, useState} from "react";
import {fetchUsageDashboard} from "@/api/usage";

export default function UsageDashboard() {
  const [usage, setUsage] = useState<any>(null);

  useEffect(() => {
    fetchUsageDashboard().then(setUsage).catch(()=>{});
  }, []);

  return (
    <pre>
      {usage ? JSON.stringify(usage, null, 2) : "Loading usage..."}
    </pre>
  );
}