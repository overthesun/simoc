//See related stack overflow answer for details 
// Site: https://stackoverflow.com/questions/24724852/pause-and-resume-setinterval/24725066 //
export function StepTimer(callback,delay){
    let timerID, start, remaining = delay

    this.pause = function(){
        window.clearTimeout(timerID)
        remaining -= Date.now() - start
    }

    this.resume = function(){
        start = Date.now()
        window.clearTimeout(timerID)
        timerID = setTimeout( () =>{
            callback()
            remaining = delay
            this.resume()    
        },remaining)
    }

    this.changeInterval = function(interval){
        window.clearTimeout(timerID)
        remaining -= Date.now() - start
        delay = interval
        this.resume()
    }
}

