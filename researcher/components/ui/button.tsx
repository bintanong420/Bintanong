import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Slot } from "@radix-ui/react-slot"

// Variants: default is the primary action (accent), outline is secondary, ghost is quiet, destructive is danger.
// Heights come from --h / --h-sm in styles.css, so every button is one height per size and 44px on phones.
const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-[length:var(--fs-base)] font-medium whitespace-nowrap transition-colors disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-[var(--accent-hover)]",
        destructive: "border border-[var(--error)] bg-transparent text-[var(--error)] hover:bg-[var(--error-bg)]",
        outline: "border border-input bg-[var(--surface)] text-foreground hover:bg-secondary",
        secondary: "bg-secondary text-foreground hover:bg-[var(--line)]",
        ghost: "text-foreground hover:bg-secondary",
        link: "text-[var(--accent)] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-[var(--h)] px-4 has-[>svg]:px-3",
        xs: "h-[var(--h-sm)] gap-1 px-2 text-[length:var(--fs-xs)] has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-[var(--h-sm)] gap-1.5 px-3 text-[length:var(--fs-sm)] has-[>svg]:px-2.5",
        lg: "h-[var(--h)] px-6 has-[>svg]:px-4",
        icon: "size-[var(--h)]",
        "icon-xs": "size-[var(--h-sm)] [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-[var(--h-sm)]",
        "icon-lg": "size-[var(--h)]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
