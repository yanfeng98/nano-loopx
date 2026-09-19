import { useLayoutEffect, useRef, useState } from "react";

import { useWorkspaceI18n } from "./i18n";

/**
 * A decision surface has to show the whole instruction it is about to write.
 * The dense task lanes keep their own bounded text; this is for the review
 * surfaces, where the Owner reads before confirming.
 *
 * Whether the text is actually clipped depends on the drawer width and the
 * script, so the disclosure is driven by measuring the rendered box rather than
 * by a character count: a short text never gains a disclosure, and a clipped
 * one always does.
 */
export function ClampedText({
  as: Element = "p",
  className,
  testId,
  text,
}: {
  as?: "h3" | "p";
  className?: string;
  testId?: string;
  text: string;
}) {
  const { t } = useWorkspaceI18n();
  const [expanded, setExpanded] = useState(false);
  const [clipped, setClipped] = useState(false);
  const bodyRef = useRef<HTMLHeadingElement & HTMLParagraphElement>(null);
  const full = text.trim();
  useLayoutEffect(() => {
    const element = bodyRef.current;
    if (!element) return;
    const measure = () => setClipped(element.scrollHeight > element.clientHeight + 1);
    measure();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => observer.disconnect();
  }, [full, expanded]);
  if (!full) return null;
  const showToggle = clipped || expanded;
  return (
    <div className={`personal-clamped-text${expanded ? " is-expanded" : ""}`} data-testid={testId}>
      <Element className={className} ref={bodyRef}>{full}</Element>
      {showToggle ? (
        <button
          aria-expanded={expanded}
          className="personal-clamp-toggle"
          onClick={() => setExpanded((value) => !value)}
          type="button"
        >
          {expanded ? t("drawer.fullTextCollapse") : t("drawer.fullTextExpand", { count: full.length })}
        </button>
      ) : null}
    </div>
  );
}
