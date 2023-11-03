import { Component, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { CloneModalComponent } from '../clone-modal/clone-modal.component'; 
import { fadeAnimation } from '../animations';

@Component({
  selector: 'app-custom-clones',
  templateUrl: './custom-clones.component.html',
  styleUrls: ['./custom-clones.component.scss'],
  animations: [fadeAnimation]
})
export class CustomClonesComponent {

  //instance variables
  cloneData: any[] = [];
  images: string[] = [];
  idleVideos: any[] = [];
  talkingVideos: any[] = [];
  cloneCount: number = 0;

  searchText= '';
  filteredClones: any[] = [];
  orderedIdleVideos: string[] = [];
  orderedTalkingVideos: string[] = [];
  isFiltering: boolean = false;

  constructor(private http: HttpClient, private sanitizer: DomSanitizer, private modalService: NgbModal) { 
    this.filteredClones = this.cloneData;
  }

  //perform initialization tasks when this component is created.
  ngOnInit() {
    
      //get all clone info from flask server
      this.http.get<any[]>('http://localhost:5000/api/get_clone_data').subscribe(data => {
          this.cloneData = data;
          this.cloneCount = this.cloneData.length;
          this.loadImagesFromData();
       });

       this.filteredClones = this.cloneData;
     
  }


  filterClones() {

      this.isFiltering = true;

      this.filteredClones = this.cloneData.filter((item) =>
        item.clone_name.toLowerCase().includes(this.searchText.toLowerCase())
      );
      // Update the ordered videos based on the filtered clones
      this.orderedIdleVideos = this.filteredClones.map((filteredClone) => {
        const index = this.cloneData.findIndex((item) => item === filteredClone);
        return this.idleVideos[index];
      });
      this.orderedTalkingVideos = this.filteredClones.map((filteredClone) => {
        const index = this.cloneData.findIndex((item) => item === filteredClone);
        return this.talkingVideos[index];
      });

  }
  

  //open modal popup 
  openPopup(item: any, idleVideo: any, talkingVideo: any) {
    const modalRef = this.modalService.open(CloneModalComponent);
    modalRef.componentInstance.item = item; // Pass clone data to modal
    modalRef.componentInstance.idleVideo = idleVideo; // Pass idleVideo data to modal
    modalRef.componentInstance.talkingVideo = talkingVideo; // Pass idleVideo data to modal

  }

  //load images from flask server 
  async loadImagesFromData() {
    for (const item of this.cloneData) {
      const imagePath = item.image_path;
      const idleVideoPath = item.idle_path;
      const talkingVideoPath = item.talking_path;
      
      const imageUrl = `http://localhost:5000/${imagePath}`;
      const idleVideoUrl = `http://localhost:5000/${idleVideoPath}`;
      const talkingVideoUrl = `http://localhost:5000/${talkingVideoPath}`;

      try {
        //push clone image into array from back end 
        const imgResponse: any = await this.http.get(imageUrl, { responseType: 'blob' }).toPromise();
        const imageBlob: Blob = imgResponse as Blob;
        const imgObjectURL = URL.createObjectURL(imageBlob);
        this.images.push(imgObjectURL);

        //push clone idle video into array from back end 
        const idleResponse: any = await this.http.get(idleVideoUrl, { responseType: 'blob' }).toPromise();
        const idleBlob: Blob = idleResponse as Blob;
        const idleObjectURL = URL.createObjectURL(idleBlob);
        const idleSafeUrl: SafeUrl = this.sanitizer.bypassSecurityTrustUrl(idleObjectURL);
        this.idleVideos.push(idleSafeUrl);

        //push clone talking video into array from back end 
        const talkingResponse: any = await this.http.get(talkingVideoUrl, { responseType: 'blob' }).toPromise();
        const talkingBlob: Blob = talkingResponse as Blob;
        const talkingObjectURL = URL.createObjectURL(talkingBlob);
        const talkingSafeUrl: SafeUrl = this.sanitizer.bypassSecurityTrustUrl(talkingObjectURL);
        this.talkingVideos.push(talkingSafeUrl);
        
        
      } catch (error) {
        console.error(`Error loading image for ${imagePath}: ${error}`);
      }
    }   
  }


}
