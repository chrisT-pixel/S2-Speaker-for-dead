import { Component, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http'; 
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-interact',
  templateUrl: './interact.component.html',
  styleUrls: ['./interact.component.scss']
})
export class InteractComponent {

  @ViewChild('videoElement', { static: false }) videoElement: ElementRef | undefined;

  textToSend: string | undefined;
  responseText: string | undefined;
  responseVideo: string | undefined;

  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef) { } 

  sendAndReceiveText(): void {
    const apiUrl = 'http://localhost:5000/api/data';  
    const data = { text: this.textToSend };

    this.http.post<any>(apiUrl, data).subscribe(
      (response) => {
        this.responseText = response.response_text; // Store the response text
        this.responseVideo = response.response_video;
        // Update the videoSource and trigger change detection
        this.responseVideo = this.responseVideo;

        // Seek to the beginning of the video and play
        this.videoElement!.nativeElement.currentTime = 0; // Seek to the beginning
        this.videoElement!.nativeElement.load(); // Load the updated video
        this.videoElement!.nativeElement.play(); // Play the updated video
        this.cdRef.detectChanges();

        
      },
      (error) => {  
        console.error('Error occurred:', error);
      }
    );
    
  }
  
}
