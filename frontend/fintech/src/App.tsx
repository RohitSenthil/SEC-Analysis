import { useState } from 'react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import axios from "axios";
import { useQuery } from '@tanstack/react-query'
import { Skeleton } from './components/ui/skeleton';

function App() {
  const backendApi = async () => {
    return axios.get("http://localhost:8000/risk", {
      params: {
        "ticker": ticker
      }
    }).then(res => res.data)
  }
  const [ticker, setTicker] = useState('')
  const { isLoading, isSuccess, isError, data, refetch } =
    useQuery({ queryKey: [ticker], queryFn: backendApi, enabled: false, refetchOnWindowFocus: false, retry: 1 });

  return (
    <div className="flex flex-col w-screen h-screen bg-black items-center gap-10 overflow-y-auto">
      <h1 className='text-white text-center text-5xl p-10'>
        SEC 10-K Risk Heat Map
      </h1>
      <div className='flex flex-row gap-8 '>
        <Input type='text' placeholder='Ticker' onChange={e => setTicker(e.target.value)} />
        <Button onClick={() => refetch()} disabled={isLoading}>Submit</Button>
      </div>
      {(() => {
        if (isLoading) {
          return <>
            <h2 className='text-white text-center text-2xl '>
              Loading, please wait...
            </h2>
            <Skeleton className="h-3/5 w-3/5 rounded-xl" />
          </>
        } else if (isError) {
          return <h2 className='text-red-700 text-center text-2xl '>
            Error, try again with another ticker
          </h2>
        } else if (isSuccess) {
          return <Loaded data={data} ticker={ticker} />
        }
        else {
          return null
        }
      })()}
    </div>
  )
}
const Loaded = (props: { data, ticker }) => {
  const { response, visualization } = props.data
  return (
    <>
      <img src={`data:image/png;base64,${visualization}`} />
      <h2 className='text-white text-center text-lg '>
        {`SEC 10-K Risk Heat Map for ${props.ticker}`}
      </h2>
      <ul className='text-white list-disc w-3/5'>
        {response.map(r => <li>{r.outcome}</li>)}
      </ul>
    </>
  )
}

export default App

