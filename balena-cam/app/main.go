package main

import (
	"fmt"
	"net/http"
	"encoding/json"
)

func handleOffer(w http.ResponseWriter, r *http.Request){
	var dat map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&dat); err != nil {
		panic(err)
	}
	//INFO: dat["sdp"] has viewer's offer sdp
	/*
	if dat["type"] == "offer" {
		fmt.Println(dat["sdp"])
	}
	*/
	answerJson := []byte(`{"hello":"world"}`)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(answerJson)
}

func main(){
	dir := http.FileServer(http.Dir("client"))
	http.Handle("/", dir)
	http.HandleFunc("/offer", handleOffer)
	fmt.Println("Server running...")
	fmt.Println("http://localhost:3000")
	http.ListenAndServe(":3000", nil)
}

