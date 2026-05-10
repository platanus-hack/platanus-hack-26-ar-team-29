import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { ChatProvider } from './contexts/ChatContext';
import './globals.css';

const geistSans = Geist({
    variable: '--font-geist-sans',
    subsets: ['latin'],
});

const geistMono = Geist_Mono({
    variable: '--font-geist-mono',
    subsets: ['latin'],
});

export const metadata: Metadata = {
    title: 'Atajo',
    description: 'Una conversación. Todas tus cuentas.',
    icons: {
        icon: '/atajo-logo.png',
        shortcut: '/atajo-logo.png',
        apple: '/atajo-logo.png',
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html
            lang='en'
            className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
        >
            <body className='min-h-full flex flex-col'>
                <ChatProvider>{children}</ChatProvider>
            </body>
        </html>
    );
}
