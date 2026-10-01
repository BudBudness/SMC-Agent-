import "./globals.css";
import type { Metadata } from "next";
export const metadata:Metadata={title:"Henryz SMC Intelligence",description:"Research-first EUR/USD market investigation workspace."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}