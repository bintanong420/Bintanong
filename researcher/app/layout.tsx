import type { Metadata } from 'next';
import './styles.css';

export const metadata: Metadata = { title: 'Bintanong | Knowledge review',
  description: 'Local institutional source review workspace.' };

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
