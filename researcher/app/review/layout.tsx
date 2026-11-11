import { ReviewShell } from '@/components/review-shell';

export default function ReviewLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <ReviewShell>{children}</ReviewShell>;
}
