import React, { useState } from 'react';
import AceEditor from 'react-ace';

// Import syntax highlighting modes
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/mode-java';

// Import themes
import 'ace-builds/src-noconflict/theme-github';
import 'ace-builds/src-noconflict/theme-monokai';

// Import editor features
import 'ace-builds/src-noconflict/ext-language_tools';

const CodeEditor = ({ onSubmit, onRun, disabled = false }) => {
  const [code, setCode] = useState('# Write your code here\n');
  const [language, setLanguage] = useState('python');
  const [theme, setTheme] = useState('monokai');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
    
    // Update starter code based on language
    switch(e.target.value) {
      case 'python':
        setCode('# Write your code here\n');
        break;
      case 'javascript':
        setCode('// Write your code here\n');
        break;
      case 'java':
        setCode('public class Solution {\n  public static void main(String[] args) {\n    // Write your code here\n  }\n}');
        break;
      default:
        setCode('# Write your code here\n');
    }
  };

  const handleThemeChange = (e) => {
    setTheme(e.target.value);
  };

  const handleCodeChange = (newCode) => {
    setCode(newCode);
  };

  const handleRun = async () => {
    if (isLoading || disabled) return;
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await onRun(code, language);
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (isLoading || disabled) return;
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await onSubmit(code, language);
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const getLanguageMode = (language) => {
    switch(language) {
      case 'javascript': return 'javascript';
      case 'java': return 'java';
      case 'python': 
      default: return 'python';
    }
  };

  return (
    <div className="code-editor">
      <div className="editor-controls">
        <div className="editor-select">
          <label htmlFor="language">Language:</label>
          <select 
            id="language"
            value={language}
            onChange={handleLanguageChange}
            disabled={disabled}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
          </select>
        </div>
        
        <div className="editor-select">
          <label htmlFor="theme">Theme:</label>
          <select 
            id="theme"
            value={theme}
            onChange={handleThemeChange}
            disabled={disabled}
          >
            <option value="monokai">Monokai</option>
            <option value="github">GitHub</option>
          </select>
        </div>
      </div>
      
      <AceEditor
        mode={getLanguageMode(language)}
        theme={theme}
        onChange={handleCodeChange}
        value={code}
        name="code-editor"
        editorProps={{ $blockScrolling: true }}
        setOptions={{
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true,
          showLineNumbers: true,
          tabSize: 2,
        }}
        fontSize={14}
        width="100%"
        height="400px"
        readOnly={disabled}
      />
      
      <div className="editor-buttons">
        <button 
          onClick={handleRun}
          className="run-btn"
          disabled={isLoading || disabled}
        >
          {isLoading ? 'Running...' : 'Run Code'}
        </button>
        
        <button 
          onClick={handleSubmit}
          className="submit-btn"
          disabled={isLoading || disabled}
        >
          {isLoading ? 'Submitting...' : 'Submit Solution'}
        </button>
      </div>

      {result && (
        <div className={`result ${result.error ? 'error' : ''}`}>
          <h3>Result</h3>
          {result.error ? (
            <div className="error-message">
              <p>Error: {result.error}</p>
            </div>
          ) : (
            <div className="result-data">
              <p>Status: {result.result?.status || 'Unknown'}</p>
              <div className="output">
                <h4>Output:</h4>
                <pre>{result.result?.output || 'No output'}</pre>
              </div>
              <p>Execution Time: {result.result?.time || 'N/A'}</p>
              <p>Memory Usage: {result.result?.memory || 'N/A'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeEditor; 