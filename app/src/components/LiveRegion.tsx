import React from "react";

type Props = {
  message: string;
  politeness?: "polite" | "assertive";
};

export default function LiveRegion({ message, politeness = "polite" }: Props) {
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="visually-hidden"
    >
      {message}
    </div>
  );
}
