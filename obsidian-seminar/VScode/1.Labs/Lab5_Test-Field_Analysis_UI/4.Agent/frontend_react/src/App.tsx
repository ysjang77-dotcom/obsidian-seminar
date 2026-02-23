import React, { useState } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import AnalysisForm from './components/AnalysisForm';
import ResultsDisplay from './components/ResultsDisplay';
import { AnalysisResult } from './types';
import './App.css';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [lifetimeColumn, setLifetimeColumn] = useState('distance(km)');
  const [typeColumn, setTypeColumn] = useState('type');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!file) {
      setError('분석할 파일을 선택해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('lifetime_column', lifetimeColumn);
    formData.append('type_column', typeColumn);

    try {
      const response = await axios.post<AnalysisResult>('http://127.0.0.1:8000/analyze/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (err: any) {
      if (axios.isAxiosError(err) && err.response) {
        setError(`분석 실패: ${err.response.data.error || err.message}`);
      } else {
        setError(`알 수 없는 오류 발생: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>브레이크 패드 수명 분석기 (React Ver.)</h1>
      </header>
      <main>
        <div className="controls">
          <FileUpload onFileSelect={setFile} />
          <AnalysisForm
            lifetimeColumn={lifetimeColumn}
            setLifetimeColumn={setLifetimeColumn}
            typeColumn={typeColumn}
            setTypeColumn={setTypeColumn}
          />
          <div className="card">
            <h3>3. 분석 실행</h3>
            <button onClick={handleSubmit} disabled={loading}>
              {loading ? '분석 중...' : '분석 실행'}
            </button>
          </div>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        {results && <ResultsDisplay results={results} />}
      </main>
    </div>
  );
};

export default App;
