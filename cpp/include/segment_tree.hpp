#ifndef SEGMENT_TREE_HPP   // 头文件保护，防止重复包含
#define SEGMENT_TREE_HPP

#include <vector>
#include <functional>

namespace Malgolab{
    template<class T,class Combine=std::function<T(const T&,const T&)>>
    class SegmentTree{
        public:
            SegmentTree(const std::vector<T> &data,T identity_,Combine combine_)
            :n(data.size()),combine(combine_),identity(identity_){
                root=NewPos();
                for(int i=0;i<n;++i){
                    insert(root,0,n-1,i,data[i]);
                }
            }
            T query(int l,int r)const{
                return query(root,0,n-1,l,r);
            }
            void modify(int x,T v){
                insert(root,0,n-1,x,v);
            }
        private:
            struct Node{
                int ls,rs;
                T dat;
                Node():ls(0),rs(0),dat(T()){}
            };
            int n,root;
            Combine combine;
            T identity;
            std::vector<Node> t;
            int NewPos(){
                t.emplace_back();
                return t.size();
            }
            void push_up(int pos){
                T lv=t[pos-1].ls?t[t[pos-1].ls-1].dat:identity;
                T rv=t[pos-1].rs?t[t[pos-1].rs-1].dat:identity;
                t[pos-1].dat=combine(lv,rv);
            }
            void insert(int &pos,int l,int r,int x,T val){
                if(!pos) pos=NewPos();
                if(l==r) return t[pos-1].dat=val,void();
                int mid((l+r)>>1);
                if(x<=mid) insert(t[pos-1].ls,l,mid,x,val);
                else insert(t[pos-1].rs,mid+1,r,x,val);
                push_up(pos);
            }
            T query(int pos,int l,int r,int ql,int qr)const{
                if(!pos) return identity;
                if(ql<=l&&r<=qr) return t[pos-1].dat;
                int mid((l+r)>>1);
                T ans(identity);
                if(ql<=mid) ans=combine(ans,query(t[pos-1].ls,l,mid,ql,qr));
                if(mid<qr) ans=combine(ans,query(t[pos-1].rs,mid+1,r,ql,qr));
                return ans;
            }
    };

} // namespace Malgolab
#endif