export interface AnalysisResult {
  message: string;
  report_url?: string;
  plot_urls?: string[];
  analysis_summary?: { [key: string]: any };
  error?: string;
}
