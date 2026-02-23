import React from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      onFileSelect(event.target.files[0]);
    }
  };

  return (
    <div className="card">
      <h3>1. 파일 업로드</h3>
      <input type="file" accept=".xlsx, .csv" onChange={handleFileChange} />
    </div>
  );
};

export default FileUpload;
