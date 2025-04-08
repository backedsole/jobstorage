import { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {

  const [jobList, setJobList] = useState()
  const [url, setUrl] = useState('')
  // const [desc, setDesc] = useState('')
  // const [company, setDesc] = useState('')
  const [error, setError] = useState('')
  const [vacancy, setVacancy] = useState()
  // const { organization = '1111' } = vacancy || {}

     // Read all jobs
    useEffect(() => {
      if (jobList) {
        return;
      }

      axios.get('http://localhost:8000/api/job')
        .then(res => {
          setJobList(res.data)
        })
    }, [jobList]); 

    //Post a job
     const addJobHandler = () => {
      axios.post('http://localhost:8000/api/job', vacancy)//{ 'title': url, 'description': desc})
      .then(res => console.log(res))
    }; 

    const parseJobHandler = () => {
      axios
        .get(`http://localhost:8000/api/parse/?url=${encodeURIComponent(url)}`)
        .then(res => {
          if (typeof res.data === 'string') {
            setError(res.data);
            setVacancy();
          } else {
            setError('');
            setVacancy(res.data);
            console.log(res);
          }
        })
    }; 

  return (
    <div className="App list-group-item justify-content-center align-items-center mx-auto" 
    style={{"width":"1000px", "backgroundColor":"white", "marginTop":"15px"}}>
      <h1 className="card text-white bg-primary mb-1" 
      style={{"maxWidth": "20rem"}}>Vacancy Storage</h1>
      <div className="card-body">
        <h5 className="card text-white bg-dark mb-3">Enter vacancy URL</h5>
        <span className="card-text">
          <input className="mb-2 form-control titleIn" placeholder='URL' 
          onChange={event => setUrl(event.target.value)}/>
          {error && <div>{error}</div>}
          <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
          "fontWeight":"bold"}} onClick={parseJobHandler}>Load vacancy</button>
          <input className="mb-2 form-control companyIn" placeholder='Company' 
          onChange={event => setVacancy({...vacancy, organization:event.target.value})} value={vacancy?.organization??""}/>
          
          <button className="btn btn-outline-primary mx-2 mb-3" style={{'borderRadius':'50px',
          "fontWeight":"bold"}} onClick={addJobHandler}>Add vacancy</button>
        </span>        
        <div dangerouslySetInnerHTML={{ __html: vacancy?.description }} style={{'textAlign': 'left'}}/>

          {/* <input className="mb-2 form-control descIn" placeholder='Description' 
          onChange={event => setVacancy({...vacancy, description:event.target.value})} value={vacancy?.description??""}/> */}
        {/* </div> */}
      </div>
    </div>
  );
}

export default App;
