import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { marked } from 'marked';
import { AnalysisResult } from '../types';

interface ResultsDisplayProps {
  results: AnalysisResult | null;
}

// 정규식 특수 문자를 이스케이프하는 함수
function escapeRegExp(string: string) {
  return string.replace(/[.*+?^${}()|[\\]/g, '\\$&'); // $&는 일치하는 전체 문자열을 의미합니다.
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [reportHtml, setReportHtml] = useState<string>('');

  useEffect(() => {
    if (results?.report_url) {
      axios.get(results.report_url, { responseType: 'text' })
        .then(response => {
          let markdownText = response.data;

          results.plot_urls?.forEach(url => {
            const filename = url.split('/').pop();
            if (filename) {
              // 파일 이름을 정규식에 사용하기 전에 이스케이프 처리합니다.
              const escapedFilename = escapeRegExp(filename);
              const regex = new RegExp(`\\(${escapedFilename}\\)`, 'g');
              markdownText = markdownText.replace(regex, `(${url})`);
            }
          });

          setReportHtml(marked(markdownText) as string);
        })
        .catch(error => {
          console.error("Error fetching or parsing report:", error);
          setReportHtml("<p>보고서 내용을 불러오는 데 실패했습니다.</p>");
        });
    }
  }, [results]);

  if (!results) {
    return null;
  }

  return (
    <div className="results-container">
      <h2>분석 결과</h2>
      
      <div className="card">
        <h3>종합 분석 보고서</h3>
        <div dangerouslySetInnerHTML={{ __html: reportHtml }} />
      </div>

      <div className="card">
        <h3>백엔드 원본 응답 (JSON)</h3>
        <pre>{JSON.stringify(results.analysis_summary, null, 2)}</pre>
      </div>
    </div>
  );
};

export default ResultsDisplay;