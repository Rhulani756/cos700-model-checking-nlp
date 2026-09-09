"use client";

import { useState } from "react";
import { CheckCircle, AlertTriangle, X, Eye, FileText, Image as ImageIcon, LayoutGrid } from "lucide-react";
import { COLORS } from "./colors";
import FeedbackSection from "./feedbackSection";

const VIEW_MODES = {
  TEXT: "text",
  GRAPHICAL: "graphical",
  COMBINED: "combined",
};

export default function Feedback({
  loading,
  stageLabel,
  assignments,
  onClosePanel,
  onPreview,
  previewOpen,
}) {
  const [viewMode, setViewMode] = useState(VIEW_MODES.COMBINED);

  const showText = viewMode === VIEW_MODES.TEXT || viewMode === VIEW_MODES.COMBINED;
  const showGraphical = viewMode === VIEW_MODES.GRAPHICAL || viewMode === VIEW_MODES.COMBINED;

  return (
    <div className={previewOpen ? "" : "lg:col-span-2"}>
      <div
        className="rounded-xl border overflow-hidden"
        style={{ borderColor: COLORS.gold, backgroundColor: COLORS.white }}
      >
        <div
          className="flex items-center justify-between px-4 py-3 border-b gap-3"
          style={{ borderColor: COLORS.goldLight, backgroundColor: COLORS.goldLight + "60" }}
        >
          <p className="text-sm font-semibold shrink-0" style={{ color: COLORS.black }}>
            Feedback
          </p>

          <div
            className="flex gap-1 p-0.5 rounded-lg border"
            style={{ borderColor: COLORS.gold, backgroundColor: COLORS.white }}
          >
            <button
              type="button"
              onClick={() => setViewMode(VIEW_MODES.TEXT)}
              aria-pressed={viewMode === VIEW_MODES.TEXT}
              title="Text only"
              className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              style={{
                backgroundColor: viewMode === VIEW_MODES.TEXT ? COLORS.gold : "transparent",
                color: viewMode === VIEW_MODES.TEXT ? COLORS.white : COLORS.gold,
              }}
            >
              <FileText className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Text</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode(VIEW_MODES.GRAPHICAL)}
              aria-pressed={viewMode === VIEW_MODES.GRAPHICAL}
              title="Diagram only"
              className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              style={{
                backgroundColor: viewMode === VIEW_MODES.GRAPHICAL ? COLORS.gold : "transparent",
                color: viewMode === VIEW_MODES.GRAPHICAL ? COLORS.white : COLORS.gold,
              }}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Diagram</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode(VIEW_MODES.COMBINED)}
              aria-pressed={viewMode === VIEW_MODES.COMBINED}
              title="Text and diagram"
              className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              style={{
                backgroundColor: viewMode === VIEW_MODES.COMBINED ? COLORS.gold : "transparent",
                color: viewMode === VIEW_MODES.COMBINED ? COLORS.white : COLORS.gold,
              }}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Both</span>
            </button>
          </div>

          <button
            type="button"
            onClick={onClosePanel}
            aria-label="Close panel"
            className="p-1 rounded-md hover:opacity-80 shrink-0"
            style={{ color: COLORS.black }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="h-96 flex flex-col items-center justify-center">
            <div className="w-12 h-12 rounded-full border-4 animate-spin mb-4" style={{ borderColor: COLORS.goldLight, borderTopColor: COLORS.blue }} />
            <p style={{ color: COLORS.black }}>{stageLabel || "Generating Feedback..."}</p>
          </div>
        ) : assignments.length === 0 ? (
          <div className="h-96 flex items-center justify-center">
            <p style={{ color: COLORS.black }}>Error Uploading Files. Please try again.</p>
          </div>
        ) : (
          <div className="space-y-8 p-4">
            {assignments.map((result, idx) => {
              const passed = result.verification_status !== "FAILED";
              const fb = result.feedback;

              return (
                <div key={idx} className="space-y-6">
                  {/* Header — always shown regardless of filter */}
                  <div
                    className="flex items-center gap-3 p-4 rounded-xl border"
                    style={{
                      borderColor: passed ? COLORS.blue : COLORS.red,
                      backgroundColor: passed ? COLORS.blueLight : COLORS.redDark + "10",
                    }}
                  >
                    {passed ? (
                      <CheckCircle className="w-6 h-6 shrink-0" style={{ color: COLORS.blue }} />
                    ) : (
                      <AlertTriangle className="w-6 h-6 shrink-0" style={{ color: COLORS.red }} />
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold truncate" style={{ color: COLORS.black }}>
                        {result.file}
                      </p>
                      <p className="text-xs" style={{ color: passed ? COLORS.blueDark : COLORS.red }}>
                        {passed
                          ? "Verification passed"
                          : `Verification failed${result.line ? ` at line ${result.line}` : ""}`}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => onPreview(result.file)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium shrink-0"
                      style={{ backgroundColor: COLORS.blue, color: COLORS.white }}
                    >
                      <Eye className="w-3.5 h-3.5" />
                      {previewOpen ? "Preview" : "Preview Code"}
                    </button>
                  </div>

                  {/* Other-files summary — always shown regardless of filter */}
                  {result.other_files && result.other_files.length > 0 && (
                    <div className="text-xs space-y-1" style={{ color: COLORS.black }}>
                      <p>
                        {result.other_files.length} other file
                        {result.other_files.length !== 1 ? "s" : ""} in this submission:
                      </p>
                      <ul className="space-y-0.5 pl-3">
                        {result.other_files.map((f) => (
                          <li key={f.file} className="flex items-center gap-1.5">
                            {f.has_feedback_error ? (
                              <span style={{ color: COLORS.red }}>⚠</span>
                            ) : f.verification_status === "FAILED" ? (
                              <span style={{ color: COLORS.red }}>✕</span>
                            ) : f.verification_status === "SUCCESSFUL" ? (
                              <span style={{ color: COLORS.blue }}>✓</span>
                            ) : (
                              <span style={{ color: COLORS.gold }}>?</span>
                            )}
                            <span className="truncate">{f.file}</span>
                            <span style={{ color: COLORS.black }}>
                              (
                              {f.has_feedback_error
                                ? "feedback error"
                                : f.verification_status === "FAILED"
                                  ? "failed"
                                  : f.verification_status === "SUCCESSFUL"
                                    ? "passed"
                                    : "unknown"}
                              )
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {!passed && showText && (result.passed_properties?.length > 0 || result.failed_properties?.length > 0 || result.undetermined_properties?.length > 0) && (
                    <FeedbackSection title="Properties Checked">
                      <ul className="space-y-1">
                        {result.failed_properties?.map((prop) => (
                          <li key={prop} className="flex items-center gap-1.5 text-sm">
                            <X className="w-3.5 h-3.5" style={{ color: COLORS.red }} />
                            <span style={{ color: COLORS.black }}>{prop}</span>
                          </li>
                        ))}
                        {result.passed_properties?.map((prop) => (
                          <li key={prop} className="flex items-center gap-1.5 text-sm">
                            <CheckCircle className="w-3.5 h-3.5" style={{ color: COLORS.blue }} />
                            <span style={{ color: COLORS.black }}>{prop}</span>
                          </li>
                        ))}
                        {result.undetermined_properties?.map((prop) => (
                          <li key={prop} className="flex items-center gap-1.5 text-sm">
                            <span style={{ color: COLORS.gold }}>?</span>
                            <span style={{ color: COLORS.black + "99" }}>{prop} (undetermined)</span>
                          </li>
                        ))}
                      </ul>
                    </FeedbackSection>
                  )}

                  {passed && showText && (
                    <>
                      <p className="text-sm" style={{ color: COLORS.black }}>
                        No violations were detected in this file.
                      </p>
                      <div>
                        <p className="text-sm" style={{ color: COLORS.black }}>
                          Properties checked:
                        </p>
                        <ul className="text-sm list-disc pl-5" style={{ color: COLORS.black }} >
                          <li>Array bounds safety</li>
                          <li>Null pointer safety</li>
                          <li>Loop termination</li>
                          <li>Division by zero</li>
                        </ul>
                      </div>
                    </>
                  )}

                  {!passed && fb && (
                    <>
                      {showText && (
                        <div>
                          <h3 className="text-lg font-bold" style={{ color: COLORS.black }}>
                            {fb.title}
                          </h3>
                          <p className="text-sm mt-1" style={{ color: COLORS.blueDark }}>
                            {fb.summary}
                          </p>
                        </div>
                      )}

                      {showText && (
                        <FeedbackSection title="Root Cause">
                          <p className="text-sm" style={{ color: COLORS.black }}>{fb.root_cause}</p>
                        </FeedbackSection>
                      )}

                      {showText && (
                        <FeedbackSection title="Evidence">
                          <ul className="list-disc list-inside space-y-1">
                            {fb.evidence.map((item, i) => (
                              <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                {item}
                              </li>
                            ))}
                          </ul>
                        </FeedbackSection>
                      )}

                      {showText && (
                        <FeedbackSection title="Execution Path">
                          <ol className="list-decimal list-inside space-y-1">
                            {fb.execution_path.map((step, i) => (
                              <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                {step}
                              </li>
                            ))}
                          </ol>
                        </FeedbackSection>
                      )}

                      {showGraphical && (
                        result.diagram_svg ? (
                          <FeedbackSection title="Execution Diagram">
                            <div
                              className="overflow-x-auto rounded-lg border p-2"
                              style={{ borderColor: COLORS.goldLight }}
                              dangerouslySetInnerHTML={{ __html: result.diagram_svg }}
                            />
                          </FeedbackSection>
                        ) : (
                          <FeedbackSection title="Execution Diagram">
                            <p className="text-sm" style={{ color: COLORS.black + "99" }}>
                              {result.diagram_render_error
                                ? `Diagram unavailable: ${result.diagram_render_error}`
                                : "No diagram available for this result."}
                            </p>
                          </FeedbackSection>
                        )
                      )}

                      {showText && (
                        <FeedbackSection title="Why It Matters">
                          <p className="text-sm" style={{ color: COLORS.black }}>{fb.why_it_matters}</p>
                        </FeedbackSection>
                      )}

                      {showText && (
                        <FeedbackSection title="Suggested Changes">
                          <ul className="list-disc list-inside space-y-1">
                            {fb.suggested_changes.map((change, i) => (
                              <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                {change}
                              </li>
                            ))}
                          </ul>
                        </FeedbackSection>
                      )}

                      {showText && fb.example_fix && (
                        <FeedbackSection title="Example">
                          <pre
                            className="text-xs p-3 rounded-lg overflow-x-auto"
                            style={{ backgroundColor: COLORS.black, color: COLORS.white }}
                          >
                            <code>{fb.example_fix}</code>
                          </pre>
                        </FeedbackSection>
                      )}

                      {showText && (
                        <div
                          className="p-4 rounded-xl border"
                          style={{ borderColor: COLORS.gold, backgroundColor: COLORS.goldLight + "60" }}
                        >
                          <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: COLORS.black }}>
                            Check Your Understanding
                          </p>
                          <p className="text-sm" style={{ color: COLORS.black }}>{fb.check_your_understanding}</p>
                        </div>
                      )}

                      {showText && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium" style={{ color: COLORS.black }}>
                            Confidence:
                          </span>
                          <span
                            className="text-xs font-semibold px-2 py-0.5 rounded-full"
                            style={{
                              backgroundColor:
                                fb.confidence === "high"
                                  ? COLORS.blueLight
                                  : fb.confidence === "medium"
                                    ? COLORS.goldLight
                                    : COLORS.redDark + "20",
                              color:
                                fb.confidence === "high"
                                  ? COLORS.blueDark
                                  : fb.confidence === "medium"
                                    ? COLORS.black
                                    : COLORS.red,
                            }}
                          >
                            {fb.confidence}
                          </span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}