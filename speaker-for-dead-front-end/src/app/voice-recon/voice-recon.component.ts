import { Component, Output, EventEmitter } from '@angular/core';
import { VoiceReconService } from '../voice-recon-service.service';

let timeoutId: any;

@Component({
  selector: 'app-voice-recon',
  templateUrl: './voice-recon.component.html',
  styleUrls: ['./voice-recon.component.scss'],
  providers: [VoiceReconService],
})
export class VoiceReconComponent {

  //inter-component communication
  @Output() voiceReconEvent = new EventEmitter<any>();

  isStartButtonDisabled: boolean = false;
  isStopButtonDisabled: boolean = true;
  prompt: string = '';

  sendPromptToParent(){
    this.voiceReconEvent.emit(this.prompt);
    console.log("emitted " + this.prompt);
  }

  //constructor passes in its service 
  constructor(private service : VoiceReconService) { 
 
    this.service.init();
    //trigger when recon service has processed incoming audio and generated the result
    this.service.recognition.onresult = (event: any) => {
    
      clearTimeout(timeoutId);
      const lastResultIndex = event.results.length - 1;
      const lastResult = event.results[lastResultIndex][0].transcript;

      // start a new timeout to stop voice recon after 1 second of silence
      timeoutId = setTimeout(() => {
        
        this.stopService();
        this.prompt = lastResult;
        this.sendPromptToParent();
        
      }, 1000);
   
    };

  }

  ngOnInit(): void {
  }

  startService(){
    this.service.start();
    this.isStartButtonDisabled = true;
    this.isStopButtonDisabled = false;
  }

  stopService(){
    this.service.stop();
  }

  stopSession(){
    this.service.stop();
    this.isStartButtonDisabled = false;
    this.isStopButtonDisabled = true;
  }

  generateText(e: string){
    this.stopService();
  }

}
