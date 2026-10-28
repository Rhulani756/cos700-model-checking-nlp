import { COLORS } from "./colors";

export default function FeedbackSection({ title, children }) {
  return (
    <div>
      <p
        className="text-xs font-semibold uppercase tracking-wide mb-2"
        style={{ color: COLORS.blueDark }}
      >
        {title}
      </p>
      {children}
    </div>
  );
}