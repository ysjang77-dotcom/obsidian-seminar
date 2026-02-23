import React from 'react';

interface AnalysisFormProps {
  lifetimeColumn: string;
  setLifetimeColumn: (value: string) => void;
  typeColumn: string;
  setTypeColumn: (value: string) => void;
}

const AnalysisForm: React.FC<AnalysisFormProps> = ({
  lifetimeColumn,
  setLifetimeColumn,
  typeColumn,
  setTypeColumn,
}) => {
  return (
    <div className="card">
      <h3>2. 분석 설정</h3>
      <div>
        <label htmlFor="lifetime_column">수명 데이터 컬럼명</label>
        <input
          id="lifetime_column"
          type="text"
          value={lifetimeColumn}
          onChange={(e) => setLifetimeColumn(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="type_column">데이터 구분 컬럼명</label>
        <input
          id="type_column"
          type="text"
          value={typeColumn}
          onChange={(e) => setTypeColumn(e.target.value)}
        />
      </div>
    </div>
  );
};

export default AnalysisForm;
