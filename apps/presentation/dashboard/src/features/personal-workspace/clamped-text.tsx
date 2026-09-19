import { useState } from "react";

import { useWorkspaceI18n } from "./i18n";

// Roughly three lines of the drawer's body text; below it the whole string is
// already visible and a disclosure would only add noise.
const CLAMP_THRESHOLD = 180;

/**
 * A decision surface has to show the whole instruction it is about to write.
 * The dense task lanes keep their own bounded text; this is for the review
 * surfaces, where the Owner reads before confirming. The element stays whatever
 * the surface already used, so only the disclosure is new.
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
  const full = text.trim();
  if (!full) return null;
  return (
    <div className={`personal-clamped-text${expanded ? " is-expanded" : ""}`} data-testid={testId}>
      <Element className={className}>{full}</Element>
      {full.length > CLAMP_THRESHOLD ? (
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
