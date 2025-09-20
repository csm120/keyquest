import React from "react";

type Props = { targetId?: string; children?: React.ReactNode };

export default function SkipLink({ targetId = "main", children = "Skip to main content" }: Props) {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    const el = document.getElementById(targetId);
    if (el) {
      // Ensure the target can take focus, then move focus there.
      el.setAttribute("tabindex", "-1");
      (el as HTMLElement).focus();
      // Remove tabindex after focus so it’s not in the tab order permanently.
      setTimeout(() => el.removeAttribute("tabindex"), 0);
    }
  };

  return (
    <a href={`#${targetId}`} className="skip-link" onClick={handleClick}>
      {children}
    </a>
  );
}
