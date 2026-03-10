#ifndef SEGMENT_TREE_HPP   // 头文件保护，防止重复包含
#define SEGMENT_TREE_HPP

#include <vector>
#include <functional>

namespace Malgolab{
    template<class T,class Combine=std::function<T(const T&,const T&)>>
    class SegmentTree{
        public:
            void SegmentTree(cosnt vector<T> &data,T identity_,Combine combine_)
            :n(data.size()),combine(combine_),identity(identity_)
            {
                t.resize(n);
            }
            void build(const vector<int> &data){
                for(int i=0;i<data.size();++i){
                    insert(1,0,n-1,i,data[i]);
                }
            }
            T query(int l,int r)const{
                return query(1,0,n-1,l,r);
            }
            void modify(int x,T v){
                insert(1,0,n-1,x,v);
            }
        private:
        #define lson t[pos-1].ls
        #define rson t[pos-1].rs
            int n;
            Combine combine;
            T identity;
            struct TREE{
                int ls,rs;
                T dat;
            };
            vector<TREE> t;
            int NewNode(){
                t.emplace_back();
                return t.size();
            }
            void push_up(int pos){
                t[pos].dat=combine(t[lson].dat,t[rson].dat);
            }
            void insert(int pos,int l,int r,int x,T val){
                if(!pos) pos=NewNode();
                if(l==x) return t[pos-1].dat=val,void();
                int mid((l+r)>>1);
                if(x<=mid) insert(lson,l,mid);
                else insert(rson,mid+1,r);
                push_up(pos-1);
            }
            T query(int pos,int l,int r,int ql,int qr)const{
                if(!pos) return identity;
                if(ql<=l&&r<=qr) return t[pos-1].dat;
                int mid((l+r)>>1);
                T ans(identity);
                if(ql<=mid) ans=combine(ans,query(lson,l,mid,ql,qr));
                if(mid<qr) ans=combine(ans,query(rson,mid+1,r,ql,qr));
                return ans;
            }
    };

} // namespace algolib
#endif