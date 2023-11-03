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

  //custom event 
  @Output() voiceReconEvent = new EventEmitter<any>();

  //instance variables
  isStartButtonDisabled: boolean = false;
  isStopButtonDisabled: boolean = true;
  prompt: string = '';

  /*sendPromptToParent(){
    this.voiceReconEvent.emit(this.prompt);
    console.log("emitted " + this.prompt);
  }*/

  sendPromptToParent() {
    if (this.isFinalResult) {
      this.voiceReconEvent.emit(this.prompt);
      console.log("Emitted: " + this.prompt);
    }
  }

  //constructor passes in its required service 
  /*constructor(private service : VoiceReconService) { 
 
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
        
      }, 1100);
   
    };

  }*/

  isFinalResult: boolean = false;

  constructor(private service: VoiceReconService) {
    // Initialize your service
    this.service.init();

    // Trigger when the recognition service has processed incoming audio and generated the result
    this.service.recognition.onresult = (event: any) => {
      clearTimeout(timeoutId);
      const lastResultIndex = event.results.length - 1;
      const isFinalResult = event.results[lastResultIndex].isFinal;
      const lastResult = event.results[lastResultIndex][0].transcript;

      // Set isFinalResult to true after 1 second of silence
      timeoutId = setTimeout(() => {
        this.isFinalResult = isFinalResult;

        // Stop the service if it hasn't stopped on its own
        if (!this.service.recognition.ended) {
          this.stopService();
        }

        this.prompt = lastResult;
        this.sendPromptToParent();
      }, 1000);
    };

    // ...
  }

  ngOnInit(): void {
  }

  //start voice recon service 
  startService(){
    this.service.start();
    this.isStartButtonDisabled = true;
    this.isStopButtonDisabled = false;
  }

  //stop voice recon service
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
