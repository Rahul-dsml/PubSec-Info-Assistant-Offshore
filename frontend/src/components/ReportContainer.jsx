import React from "react";
import ReactMarkdown from "react-markdown";
import {useTranslation} from "react-i18next";
const ReportContainer = ({ data }) => {

  const {t} = useTranslation()
  const language = t("translation.code") 
  return (
    <div className="max-w-3xl mx-auto p-6 bg-transparent  space-y-6" dir={language === "ar" ? "rtl" : "ltr"} style={{ textAlign: isRTL ? "right" : "left" }} >
      <section className={""}>
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl text-cyan-300 font-bold mb-2">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl text-cyan-300 font-semibold mb-2">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg text-cyan-300 font-medium mb-2">
                {children}
              </h3>
            ),

            a: ({ children }) => (
              <a target="_blank" className="text-cyan-600 hover:underline">
                {children}
              </a>
            ),
          }}
          className="prose prose-lg"
        >
          {data.Current_apartment_details}
        </ReactMarkdown>
      </section>

      <section className="">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl text-cyan-300 font-bold mb-2">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl text-cyan-300 font-semibold mb-2">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg text-cyan-300 font-medium mb-2">
                {children}
              </h3>
            ),

            a: ({ children }) => (
              <a target="_blank" className="text-cyan-600 hover:underline">
                {children}
              </a>
            ),
          }}
          className="prose prose-lg"
        >
          {data.Comparison}
        </ReactMarkdown>
      </section>

      <section className="">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl text-cyan-300 font-bold mb-2">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl text-cyan-300 font-semibold mb-2">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg text-cyan-300 font-medium mb-2">
                {children}
              </h3>
            ),

            a: ({ children }) => (
              <a target="_blank" className="text-cyan-600 hover:underline">
                {children}
              </a>
            ),
          }}
          className="prose prose-lg"
        >
          {data.Summary}
        </ReactMarkdown>
      </section>

      <section className="">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-3xl text-cyan-300 font-bold mb-2">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl text-cyan-300 font-semibold mb-2">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg text-cyan-300 font-medium mb-2">
                {children}
              </h3>
            ),

            a: ({ children }) => (
              <a target="_blank" className="text-cyan-600 hover:underline">
                {children}
              </a>
            ),
          }}
          className="prose prose-lg"
        >
          {data.Recommendations}
        </ReactMarkdown>
      </section>
    </div>
  );
};

export default ReportContainer;
