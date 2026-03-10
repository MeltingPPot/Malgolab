#include<iostream>
#include<vector>
#include "segment_tree.hpp"

using namespace std;
using namespace Malgolab;

int main(){
    int n;
    cin>>n;
    vector<int> arr(n);
    for(int i=0;i<n;++i) cin>>arr[i];

    SegmentTree<int> seg(arr);
    
    char opt;
    while(cin>>opt){
        if(opt=='Q'){
            int l,r;
            cin>>l>>r;
            cout<<seg.query(l,r)<<endl;
        }else{
            int x,v;
            cin>>x>>v;
            seg.modify(x,v);
        }
    }
}