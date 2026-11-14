export function BrandMark({ size = 28, className = "", alt = "" }: { size?: number; className?: string; alt?: string }) {
  return <span className={`brand-mark ${className}`} style={{ inlineSize: size, blockSize: size }}><img src="/brand/bintanong-logo.png" alt={alt} /></span>;
}
