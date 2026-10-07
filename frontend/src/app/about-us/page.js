"use client";

import Link from "next/link";
import { COLORS } from "../components/colors";

const TEAM_MEMBERS = ["u20463104", "u21507067", "u23875616", "u26071135"];

export default function AboutUs() {
  return (
    <div className="flex-1 min-h-0 flex flex-col bg-white font-sans">
      <header className="border-b-4" style={{ backgroundColor: COLORS.black, borderColor: COLORS.gold }}>
        <div className="px-12 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tight text-white">
                Team &amp; Organisation
              </h1>
              <p className="text-sm font-medium tracking-wide" style={{ color: COLORS.gold }}>
                About This Research
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto px-6 py-12 w-full space-y-10">
        <section className="space-y-2">
          <h2 className="text-2xl font-bold" style={{ color: COLORS.black }}>
            Integrating Model Checking and NLP to Provide Pedagogic
            Feedback on Programming Assignments
          </h2>
          <p className="text-sm" style={{ color: COLORS.black + "99" }}>
            A research project undertaken at the University of Pretoria
          </p>
        </section>

        <section
          className="rounded-xl border overflow-hidden"
          style={{ borderColor: COLORS.gold, backgroundColor: COLORS.goldLight + "40" }}
        >
          <div className="px-6 py-5 grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <p
                className="text-xs font-semibold uppercase tracking-wide mb-1"
                style={{ color: COLORS.blueDark }}
              >
                Supervisor
              </p>
              <p className="text-base font-medium" style={{ color: COLORS.black }}>
                Prof. Nils Timm
              </p>
            </div>

            <div>
              <p
                className="text-xs font-semibold uppercase tracking-wide mb-2"
                style={{ color: COLORS.blueDark }}
              >
                Team Members
              </p>
              <ul className="space-y-1">
                {TEAM_MEMBERS.map((member) => (
                  <li
                    key={member}
                    className="text-sm font-mono"
                    style={{ color: COLORS.black }}
                  >
                    {member}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-lg font-bold" style={{ color: COLORS.black }}>
            About the Research
          </h3>

          <p className="text-sm leading-relaxed" style={{ color: COLORS.black }}>
            Automated assessment of programming assignments is widely used in
            computer science education, but the feedback provided to
            students is often limited to test-case failures or low-level
            error messages.{" "}
            <a
              href="https://en.wikipedia.org/wiki/Model_checking"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:opacity-80"
              style={{ color: COLORS.blue }}
            >
              Model checking
            </a>{" "}
            offers the potential to analyse program behaviour more
            systematically and to detect logical errors that go beyond
            simple input&ndash;output mismatches. However, the output
            produced by model checkers is typically highly technical and
            difficult for students to interpret.
          </p>

          <p className="text-sm leading-relaxed" style={{ color: COLORS.black }}>
            The objective of this project is to investigate the use of
            model checking for generating automated feedback on programming
            assignments and to enhance the pedagogic usability of this
            feedback through natural language processing (NLP) techniques.
            Given a formal specification of expected program behaviour and
            a student submission, model checking can be used to identify
            violations of correctness properties. The resulting
            counterexamples or diagnostic information are then transformed
            into human-readable feedback that explains the nature of the
            error in a way that is accessible to novice programmers.
          </p>

          <p className="text-sm leading-relaxed" style={{ color: COLORS.black }}>
            The major objective of this project is the design of a
            feedback generation framework that maps model checking results
            to structured natural language explanations. The effectiveness
            of the framework in enhancing students&rsquo; learning
            experience is evaluated through experiments with students.
          </p>
        </section>

        <section
          className="text-xs pt-4 border-t"
          style={{ borderColor: COLORS.goldLight, color: COLORS.black + "88" }}
        >
          <p>
            [1]{" "}
            <a
              href="https://en.wikipedia.org/wiki/Model_checking"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:opacity-80"
              style={{ color: COLORS.blueDark }}
            >
              https://en.wikipedia.org/wiki/Model_checking
            </a>
          </p>
        </section>
      </main>

      <footer className="mt-auto border-t-4" style={{ backgroundColor: COLORS.black, borderColor: COLORS.gold }}>
        <div className="py-7">
          <ul className="flex flex-row justify-center gap-6 list-none">
            <li>
              <Link href="/" className="text-white hover:text-blue-500">
                Home
              </Link>
            </li>
          </ul>
        </div>
      </footer>
    </div>
  );
}