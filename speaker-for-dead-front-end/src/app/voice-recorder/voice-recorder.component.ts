import { Component, EventEmitter, Output } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
// @ts-ignore
import * as RecordRTC from 'recordrtc';


@Component({
  selector: 'app-voice-recorder',
  templateUrl: './voice-recorder.component.html',
  styleUrls: ['./voice-recorder.component.scss']
})
export class VoiceRecorderComponent {
  
  record: any;
  recording = false;
  fileUrl: any;
  error: any;

  @Output() fileUrlEvent = new EventEmitter<string>();
  
  constructor(private domSanitizer: DomSanitizer) {}

  sanitize(url: string) {
    return this.domSanitizer.bypassSecurityTrustUrl(url);
  }
  
  //Start recording.
  initiateRecording() {
    this.recording = true;
    let mediaConstraints = {
      video: false,
      audio: true
    };
    navigator.mediaDevices.getUserMedia(mediaConstraints).then(this.successCallback.bind(this), this.errorCallback.bind(this));
  }
  /**
  * Will be called automatically.
  */
  successCallback(stream: any) {
    var options = {
    mimeType: "audio/mp3",
    numberOfAudioChannels: 1,
    bufferSize: 16384,
    };
    //Start Actual Recording
    var StereoAudioRecorder = RecordRTC.StereoAudioRecorder;
    this.record = new StereoAudioRecorder(stream, options);
    this.record.record();
    }
  /**
  * Stop recording.
  */
  stopRecording() {
    this.recording = false;
    this.record.stop(this.processRecording.bind(this));
  }

  /**
  * processRecording Do what ever you want with blob
  * @param  {any} blob Blog
  */
  processRecording(blob: any) {
    this.fileUrl = URL.createObjectURL(blob);
    console.log("blob", blob);
    console.log("url", this.fileUrl);
    // Emit the fileUrl to the parent component
    this.fileUrlEvent.emit(this.fileUrl); 

  }
  //Process Error.
  errorCallback(error: any) {
    this.error = 'Can not play audio in your browser';
  }
  ngOnInit() {}

}
