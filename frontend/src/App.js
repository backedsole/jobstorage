import { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css'

const categories = [
  "SysAdmin",
  "DevOps",
  "QA",
  "Dev",
  "Support",
  "Other",
]

const englishLevels = [
  "None",
  "A1-B1 a plus",
  "B2-C1 a plus",
  "A1-B1",
  "B2-C1",
]

function parseTags(str) {
  return str.split(',').map((s) => s.trim()).filter((v) => v);
}

function stringifyTags(tags = []) {
  
}

function App() {

  const [jobList, setJobList] = useState()
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [vacancy, setVacancy] = useState({})
  const [duplicates, setDuplicates] = useState()

     // Read all jobs
    // useEffect(() => {
    //   if (jobList) {
    //     return;
    //   }

    //   axios.get('http://localhost:8000/api/job')
    //     .then(res => {
    //       setJobList(res.data)
    //     })
    // }, [jobList]); 

    // Add job to database
    const addJobHandler = () => {
      vacancy.addedToBase = new Date().toISOString();
      axios.post('http://localhost:8000/api/job', { ...vacancy, url: url})
      .then(res => console.log(res))
    };

    // Add parsed vacancy as duplicate to existing one in database
    const addDuplicateHandler = (dupUrl) => {
      axios.post('http://localhost:8000/api/job/duplicate', { duplicateUrl: vacancy.url[0], url: dupUrl })
      .then(res => console.log(res))
    };

    // Get job info from vacancy url
    const parseJobHandler = () => {
      axios
        .get(`http://localhost:8000/api/parse/?url=${encodeURIComponent(url)}`)
        .then(res => {
          setError(res.data.msg);
          setDuplicates(res.data.duplicates);
          setVacancy(res.data.vacancy);
          console.log(res);
        })
    }; 

  return (
    <div className="App list-group-item justify-content-center align-items-center mx-auto" 
    style={{"width":"1000px", "backgroundColor":"white", "marginTop":"15px"}}>
      <h1 className="card text-white bg-primary mb-1" 
      style={{"maxWidth": "20rem"}}>Vacancy Storage</h1>
      <div className="card-body">
        <div className="card-text">
          <input className="mb-2 form-control" placeholder='Enter vacancy URL' 
          onChange={event => setUrl(event.target.value)}/>
          { error && 
            <div class="alert alert-info" role="alert">
              {error}
              {error === "Already in database" &&
                <>.  Added: { new Date(vacancy.addedToBase).toDateString()}</>
              }
            </div>
          }
          <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
          "fontWeight":"bold"}} onClick={parseJobHandler}>Load vacancy</button>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor="added">Added: {vacancy?.addedOnSite??""}    </label>
            <label htmlFor="site">Job Site: {vacancy?.site??""}    </label>
            <label htmlFor="category">Choose category:</label>
            <select
              id="category"
              onChange={event => setVacancy({ ...vacancy, category: event.target.value })}
              value={vacancy?.category}
              className="form-select" style={{ width: 'auto' }}
            >
              {categories.map((category) => (
                <option value={category}  key={category}>{category}</option>
              ))}
            </select>
            <label htmlFor="englishLevel">English level:</label>
            <select 
              id="englishLevel"
              onChange={event => setVacancy({ ...vacancy, englishLevel: event.target.value })}
              value={vacancy?.englishLevel}
              className="form-select"  style={{ width: 'auto' }}
            >
              {englishLevels.map((englishLevel) => (
                <option value={englishLevel} key={englishLevel}>{englishLevel}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
          "fontWeight":"bold"}} onClick={addJobHandler}>Add to database</button>
          {duplicates && 
            <>
              <h5 className="card text-white bg-dark mb-3">Possible duplicates</h5>
              {duplicates.map((dup) => (
                <div >
                  <a href={dup.url} target="_blank" rel="noreferrer">{dup.url}</a>
                  <button className="btn btn-primary" style={{'borderRadius':'50px',
                  "fontWeight":"bold"}} onClick={() => addDuplicateHandler(dup.url)}>Add as duplicate</button>
                </div>
              ))}
            </>
          }
          <h5 className="card text-white bg-dark mb-3">Details</h5>
          <div className="d-flex align-items-center column-gap-3 flex-wrap">
            <label htmlFor='Tags'>Tags: </label>
            {(vacancy?.tags || []).map((tag, index) => 
              <button
                className="btn btn-outline-danger"
                onClick={() => setVacancy({...vacancy, tags: (vacancy.tags ?? []).toSpliced(index, 1)})}
              >
                {tag}
              </button>
            )}
            <input className="form-control" style={{flexShrink: 1, flexGrow: 1, width: 'auto'}} placeholder='Tags' 
              onKeyUp={event => {
                if (event.key !== 'Enter') {
                  return;
                }

                const tags = vacancy?.tags ?? [];
                const tag = event.target.value.trim();

                event.target.value = '';

                if (!tag || tags.indexOf(tag) !== -1) {
                  return;
                }
                
                // setVacancy({...vacancy, tags: [...tags, tag]});
                setVacancy({...vacancy, tags: [...tags, tag].sort()});
              }}
            />
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Position'>Position: </label>
            <input className="form-control" placeholder='Position' 
            onChange={event => setVacancy({...vacancy, position:event.target.value})} value={vacancy?.position??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Company'>Company: </label>
            <input className="form-control" placeholder='Company' 
            onChange={event => setVacancy({...vacancy, organization:event.target.value})} value={vacancy?.organization??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Salary'>Salary: </label>
            <input className="form-control" placeholder='Salary' 
            onChange={event => setVacancy({...vacancy, salary:event.target.value})} value={vacancy?.salary??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Conditions'>Conditions: </label>
            <input className="form-control" placeholder='Conditions' 
            onChange={event => setVacancy({...vacancy, conditions:event.target.value})} value={vacancy?.conditions??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Contacts'><b>Contacts: </b></label>
            <input className="form-control" placeholder='Contacts' 
            onChange={event => setVacancy({...vacancy, recruiterContacts:event.target.value})} value={vacancy?.recruiterContacts??""}/>
          </div>
        </div>        

        <h5 className="card text-white bg-dark mb-3">Description</h5>
        <div dangerouslySetInnerHTML={{ __html: vacancy?.description }} style={{'textAlign': 'left'}}/>
      </div>
    </div>
  );
}

export default App;
