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
  const [mainVacancy, setMainVacancy] = useState({})
  const [duplicates, setDuplicates] = useState()
  const [popupVacancy, setPopupVacancy] = useState()
  const vacancy = popupVacancy || mainVacancy;
  const isPopup = !!popupVacancy;

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
    const addDuplicateHandler = (dupId) => {
      axios.post('http://localhost:8000/api/job/duplicate', { duplicateUrl: vacancy.url, id: dupId })
      .then(res => console.log(res))
    };

    // Get job info from vacancy url
    const parseJobHandler = () => {
      axios
        .get(`http://localhost:8000/api/parse/?url=${encodeURIComponent(url)}`)
        .then(res => {
          setError(res.data.msg);
          setDuplicates(res.data.duplicates);
          setMainVacancy({...res.data.vacancy, category: 'SysAdmin', englishLevel: 'None'});
          console.log(res);
        })
    }; 

    // Open Main vacancy details
    const showMainJobHandler = (dupId) => {
      if (!dupId) {
        setPopupVacancy();
        return;
      }

      //Open details in separate tab
      axios.get(`http://localhost:8000/api/job/main?jobId=${dupId}`)
        .then(res => {
          console.log(res);
          setError(res.data.msg);
          setPopupVacancy(res.data);
        })
    };

    // Load Main Vacancy details
    const LoadMainJobHandler = (jobId) => {
      axios.get(`http://localhost:8000/api/job/?jobId=${jobId}`)
        .then(res => {
          setError(res.data.msg);
          setDuplicates(null);
          setMainVacancy(res.data.vacancy);       
        })
    };

    // Load Site Vacancy details
    const LoadSiteJobHandler = (jobId) => {
      axios.get(`http://localhost:8000/api/job/?jobId=${encodeURIComponent(url)}`)
        .then(res => {
          setError(res.data.msg);
          setDuplicates(null);
          setMainVacancy(res.data.vacancy);       
        })
    };

  return (
    <div className="App list-group-item justify-content-center align-items-center mx-auto" 
    style={{"width":"1000px", "backgroundColor":"white", "marginTop":"15px"}}>
      {isPopup && <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
          "fontWeight":"bold"}} onClick={() => showMainJobHandler()}>Back</button>}
      <h1 className="card text-white bg-primary mb-1" 
      style={{"maxWidth": "20rem"}}>Vacancy Storage</h1>
      <div className="card-body">
        <div className="card-text">
          {!isPopup && 
            <>
              <input className="mb-2 form-control" placeholder='Enter vacancy URL' 
                onChange={event => setUrl(event.target.value)} value={url}/>
              { error && 
                <div class="alert alert-info" role="alert">
                  {error}
                  {error === "Already in database" &&
                    <>.  Added: { new Date(vacancy.addedToBase).toDateString()}
                    <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
                      "fontWeight":"bold"}} onClick={LoadMainJobHandler()}>Load Main Vacancy</button>
                    </>
                  }
                </div>
              }
              <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
              "fontWeight":"bold"}} onClick={parseJobHandler}>Load vacancy</button>
            </>
          }
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor="added">Added: {vacancy?.addedOnSite??""}    </label>
            <label htmlFor="site">Job Site: {vacancy?.site??""}    </label>
            <label htmlFor="category">Choose category:</label>
            <select
              id="category"
              onChange={event => setMainVacancy({ ...vacancy, category: event.target.value })}
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
              onChange={event => setMainVacancy({ ...vacancy, englishLevel: event.target.value })}
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

          {/* {vacancy?.originalUrls &&
            <>
            <h5 className="card text-white bg-dark mb-3">Possible duplicates</h5>
            {vacancy.originalUrls.map((url) => (

              <div>
                <a href={dup.url} target="_blank" rel="noreferrer">{dup.url}</a>
                <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
                "fontWeight":"bold"}} onClick={LoadSiteJobHandler(url)}>Load Site Vacancy</button>
              </div>
            
            {duplicates.map((dup) => (
              <div >
                <label htmlFor='Position'>{dup.position} </label>
                <label htmlFor='Company'>{dup.organization} </label>
                {dup.site === 'Main' &&
                  <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
                  "fontWeight":"bold"}} onClick={showMainJobHandler(dup.id)}>Main</button>
                }
                {!dup.site &&
                  <>
                    <a href={dup.url} target="_blank" rel="noreferrer">{dup.url}</a>
                    
                  </>
                }
                <button className="btn btn-primary" style={{'borderRadius':'50px',
                "fontWeight":"bold"}} onClick={() => addDuplicateHandler(dup.id)}>Add as duplicate</button>
              </div>
            ))}
          </>          

          } */}
          {duplicates && !isPopup && 
            <>
              <h5 className="card text-white bg-dark mb-3">Possible duplicates</h5>
              {duplicates.map((dup) => (
                <div key={dup.id}>
                  <label htmlFor='Position'>{dup.position} </label>
                  <label htmlFor='Company'>{dup.organization} </label>
                  {dup.site === 'Main' &&
                    <button className="btn btn-outline-primary mx-2" style={{'borderRadius':'50px',
                    "fontWeight":"bold"}} onClick={() => showMainJobHandler(dup.id)}>Main</button>
                  }
                  {!dup.site &&
                    <>
                      <a href={dup.url} target="_blank" rel="noreferrer">{dup.url}</a>
                      
                    </>
                  }
                  <button className="btn btn-primary" style={{'borderRadius':'50px',
                  "fontWeight":"bold"}} onClick={() => addDuplicateHandler(dup.id)}>Add as duplicate</button>
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
                onClick={() => setMainVacancy({...vacancy, tags: (vacancy.tags ?? []).toSpliced(index, 1)})}
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
                setMainVacancy({...vacancy, tags: [...tags, tag].sort()});
              }}
            />
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Position'>Position: </label>
            <input className="form-control" placeholder='Position' 
            onChange={isPopup ? undefined : event => setMainVacancy({...vacancy, position:event.target.value})} value={vacancy?.position??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Company'>Company: </label>
            <input className="form-control" placeholder='Company' 
            onChange={event => setMainVacancy({...vacancy, organization:event.target.value})} value={vacancy?.organization??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Salary'>Salary: </label>
            <input className="form-control" placeholder='Salary' 
            onChange={event => setMainVacancy({...vacancy, salary:event.target.value})} value={vacancy?.salary??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Conditions'>Conditions: </label>
            <input className="form-control" placeholder='Conditions' 
            onChange={event => setMainVacancy({...vacancy, conditions:event.target.value})} value={vacancy?.conditions??""}/>
          </div>
          <div className="d-flex align-items-center column-gap-3">
            <label htmlFor='Contacts'><b>Contacts: </b></label>
            <input className="form-control" placeholder='Contacts' 
            onChange={event => setMainVacancy({...vacancy, recruiterContacts:event.target.value})} value={vacancy?.recruiterContacts??""}/>
          </div>
        </div>        

        <h5 className="card text-white bg-dark mb-3">Description</h5>
        <div dangerouslySetInnerHTML={{ __html: vacancy?.description }} style={{'textAlign': 'left'}}/>
      </div>
    </div>
  );
}

export default App;
